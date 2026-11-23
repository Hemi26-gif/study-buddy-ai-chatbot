"""LangChain + Groq logic for StudyBuddy (no Streamlit code in here)."""
import json
import re
from datetime import date, timedelta

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

# --------------------------------------------------------------------------
# Prompts (passed to LangChain as *variables*, so braces in notes/code are safe)
# --------------------------------------------------------------------------
CHAT_SYSTEM = (
    "You are Mimi, a cheerful and patient AI study buddy (a friendly doll mascot) "
    "inside the StudyBuddy app. Teach like a great tutor: start with a one-line simple "
    "definition, explain step by step in plain language, give 1-3 practical examples "
    "(use fenced code blocks for code), mention common mistakes, and finish with a short "
    "recap and one follow-up question. The final line must be exactly one concise question "
    "ending in a question mark; never omit it. Use a warm tone with a few emojis but stay focused. "
    "If the student asks for a full quiz, a big set of MCQs or a study schedule, give a "
    "brief answer and tell them to use the Quiz, MCQ or Planner tabs. "
    "If you are unsure about something, say so instead of guessing."
)

PLAN_SYSTEM = (
    "You are an expert learning coach. Create a realistic, motivating study schedule. "
    "Generate only the requested days, using a heading in this exact format for each day: "
    "'### Day N - YYYY-MM-DD (Weekday)'. Under each heading, put the focus, tasks as "
    "separate Markdown bullet lines, and the time. Never use a Markdown table or HTML, "
    "including <br> tags. Respect the requested hours per day, include practice tasks, "
    "make every seventh day a revision day, and include a mini self-test on the final day."
)

MCQ_SYSTEM = (
    "You are an expert exam-setter. Return ONLY a valid JSON array - no markdown fences, "
    "no commentary. Each item must be an object with exactly these keys: "
    '"question" (string), "options" (array of exactly 4 short strings WITHOUT letter '
    'prefixes like "A."), "answer_index" (integer 0-3), "explanation" (1-2 sentences). '
    "Make distractors plausible, vary the position of the correct answer, and avoid "
    "'all of the above'."
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def get_llm(api_key: str, model: str, temperature: float = 0.4) -> ChatGroq:
    return ChatGroq(model=model, groq_api_key=api_key, temperature=temperature)


def to_text(content) -> str:
    """Normalize a model response to a string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                parts.append(p.get("text", ""))
        return "".join(parts)
    return str(content)


def notes_section(notes: str) -> str:
    if not notes:
        return ""
    return (
        "\n\nThe student uploaded study notes. Use them as the primary source. "
        "If something is not covered in them, say so, then help with general knowledge.\n"
        "--- NOTES START ---\n" + notes[:24000] + "\n--- NOTES END ---"
    )


def friendly_error(e: Exception) -> str:
    msg = str(e)
    low = msg.lower()
    if any(k in low for k in ("api key", "api_key", "401", "403", "permission")):
        hint = "Your Groq API key looks invalid or lacks access."
    elif any(k in low for k in ("429", "quota", "resource_exhausted", "rate")):
        hint = "Rate limit reached - wait a minute and try again."
    elif "404" in low or "not found" in low:
        hint = (
            "Groq doesn't recognize that model ID or your account can't access it. "
            "Choose an active model shown in your Groq console and enter its exact ID in the sidebar."
        )
    else:
        hint = "Check your API key, model name and internet connection."
    return f"{hint}\n\nDetails: {msg[:300]}"


# --------------------------------------------------------------------------
# 1) Chat / explain concepts (streaming + memory)
# --------------------------------------------------------------------------
def chat_stream(question, history, api_key, model, notes):
    """Yield text chunks. `history` = list of {"role","content"} dicts."""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system}"),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )
    msgs = []
    for m in history[-10:]:
        cls = HumanMessage if m["role"] == "user" else AIMessage
        msgs.append(cls(content=m["content"]))

    chain = prompt | get_llm(api_key, model, 0.4)
    for chunk in chain.stream(
        {"system": CHAT_SYSTEM + notes_section(notes), "history": msgs, "question": question}
    ):
        text = to_text(chunk.content)
        if text:
            yield text


# --------------------------------------------------------------------------
# 2) Study schedule
# --------------------------------------------------------------------------
def generate_schedule(subject, goal, level, days, hours, start, extra, api_key, model, notes):
    context = (
        f"Subject / topic: {subject}\n"
        f"Goal: {goal or 'Learn it well'}\n"
        f"Current level: {level}\n"
        f"Days available: {days}\n"
        f"Hours per day: {hours}\n"
        f"Start date: {start}\n"
        f"Extra notes: {extra or 'None'}"
    )
    prompt = ChatPromptTemplate.from_messages([("system", "{system}"), ("human", "{request}")])
    chain = prompt | get_llm(api_key, model, 0.5)
    first_day = date.fromisoformat(start)
    schedule_parts = []

    for batch_start in range(1, days + 1, 10):
        batch_end = min(batch_start + 9, days)
        batch_dates = "\n".join(
            f"Day {day_number}: {(first_day + timedelta(days=day_number - 1)).isoformat()} "
            f"({(first_day + timedelta(days=day_number - 1)).strftime('%A')})"
            for day_number in range(batch_start, batch_end + 1)
        )
        request = (
            f"{context}\n"
            f"Generate exactly days {batch_start} through {batch_end}, using these dates:\n"
            f"{batch_dates}\n"
        )
        if batch_start == 1:
            request += "Start with a 2-3 line overview before the day headings.\n"
        if batch_end == days:
            request += "Finish with 4 short study tips after the day entries.\n"

        result = chain.invoke(
            {"system": PLAN_SYSTEM + notes_section(notes), "request": request}
        )
        batch_text = re.sub(r"<br\s*/?>", "\n", to_text(result.content), flags=re.IGNORECASE)
        generated_days = {
            int(day_number)
            for day_number in re.findall(r"(?im)^#{1,3}\s*Day\s+(\d+)\b", batch_text)
        }
        expected_days = set(range(batch_start, batch_end + 1))
        if generated_days != expected_days:
            missing_days = sorted(expected_days - generated_days)
            raise ValueError(
                f"The schedule response did not include every requested day. "
                f"Missing days: {', '.join(map(str, missing_days)) or 'none'}."
            )
        schedule_parts.append(batch_text.strip())

    return "\n\n".join(schedule_parts)


# --------------------------------------------------------------------------
# 3 + 4) MCQs and quizzes (same generator, different UI)
# --------------------------------------------------------------------------
def _extract_json_array(text: str):
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array found in the model reply.")
    return json.loads(text[start : end + 1])


def _clean_questions(raw):
    cleaned = []
    for item in raw:
        try:
            opts = [re.sub(r"^[A-Da-d][\).:]\s+", "", str(o).strip()) for o in item["options"]]
            ans = int(item["answer_index"])
            q = str(item["question"]).strip()
            if q and len(opts) == 4 and 0 <= ans < 4:
                cleaned.append(
                    {
                        "question": q,
                        "options": opts,
                        "answer_index": ans,
                        "explanation": str(item.get("explanation", "")).strip(),
                    }
                )
        except (KeyError, TypeError, ValueError):
            continue
    return cleaned


def generate_mcqs(topic, count, difficulty, api_key, model, notes):
    """Return a list of validated MCQ dicts."""
    prompt = ChatPromptTemplate.from_messages([("system", "{system}"), ("human", "{request}")])
    chain = prompt | get_llm(api_key, model, 0.5)
    request = f"Create {count} {difficulty.lower()} multiple-choice questions on: {topic}"

    last_error = None
    for _ in range(2):  # one retry if the JSON is malformed
        try:
            result = chain.invoke(
                {"system": MCQ_SYSTEM + notes_section(notes), "request": request}
            )
            questions = _clean_questions(_extract_json_array(to_text(result.content)))
            if questions:
                return questions
        except (ValueError, json.JSONDecodeError) as e:
            last_error = e
    raise ValueError(f"Could not generate valid questions. {last_error or ''}")
