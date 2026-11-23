import os
import re
import uuid
import base64
from datetime import date
from io import BytesIO
from pathlib import Path

import streamlit as st  # pyright: ignore[reportMissingImports]
from docx import Document  # pyright: ignore[reportMissingImports]
from pypdf import PdfReader  # pyright: ignore[reportMissingImports]
from streamlit.errors import StreamlitSecretNotFoundError  # pyright: ignore[reportMissingImports]

import ai_engine as ai
from ui_theme import hero_html, inject_css

MIMI_AVATAR_PATH = Path(__file__).resolve().parent / "assets" / "mimi-avatar.svg"
MIMI_AVATAR = "data:image/svg+xml;base64," + base64.b64encode(
    MIMI_AVATAR_PATH.read_bytes()
).decode("ascii")

MODEL_DEFAULT = "openai/gpt-oss-20b"
MODEL_WITH_NOTES = "qwen/qwen3.8-27b"
MODEL_WITHOUT_NOTES = "openai/gpt-oss-120b"
MODEL_OPTIONS_WITHOUT_NOTES = [MODEL_DEFAULT, MODEL_WITHOUT_NOTES]
MODEL_OPTIONS_WITH_NOTES = [MODEL_DEFAULT, MODEL_WITH_NOTES, MODEL_WITHOUT_NOTES]


def load_dotenv() -> None:
    """Load basic KEY=VALUE settings from a sibling .env file without a dependency."""
    env_path = Path(__file__).resolve().parent / ".env"
    try:
        lines = env_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not key or key in os.environ:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        else:
            value = value.split("#", 1)[0].rstrip()
        os.environ[key] = value


load_dotenv()
st.set_page_config(page_title="StudyBuddy – AI Study Assistant", page_icon="🎓", layout="wide")
inject_css()


def get_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if api_key:
        return api_key
    try:
        return str(st.secrets.get("GROQ_API_KEY", "")).strip()
    except StreamlitSecretNotFoundError:
        return ""


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
GREETING = "Hi! I'm Mimi, your study buddy! Ask me anything or pick a tab below ✨"
DEFAULTS = {
    "messages": [],
    "document_text": "",
    "document_name": "",
    "mood": "idle",
    "doll_msg": GREETING,
    "pending": None,
    "schedule": None,
    "mcqs": None,
    "mcq_topic": "",
    "quiz": None,
    "model_selection": MODEL_DEFAULT,
    "upload_widget_version": 0,
    "groq_api_key_override": "",
    "chat_follow_up": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# The doll lives in a placeholder so we can change her mood while the app is working
doll_slot = st.empty()
doll_slot.markdown(hero_html(st.session_state.mood, st.session_state.doll_msg), unsafe_allow_html=True)


def set_doll(mood: str, message: str) -> None:
    st.session_state.mood = mood
    st.session_state.doll_msg = message
    doll_slot.markdown(hero_html(mood, message), unsafe_allow_html=True)


def read_notes(file) -> str:
    filename = file.name.lower()
    if filename.endswith(".pdf"):
        reader = PdfReader(BytesIO(file.getvalue()))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    if filename.endswith(".docx"):
        document = Document(BytesIO(file.getvalue()))
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    return file.getvalue().decode("utf-8", errors="ignore")


def sync_model_with_upload(upload_key: str) -> None:
    uploaded_file = st.session_state.get(upload_key)
    if uploaded_file is None:
        st.session_state.document_text = ""
        st.session_state.document_name = ""
        st.session_state.model_selection = MODEL_WITHOUT_NOTES
    else:
        st.session_state.document_text = ""
        st.session_state.document_name = ""
        st.session_state.model_selection = MODEL_WITH_NOTES


def remove_notes() -> None:
    st.session_state.document_text = ""
    st.session_state.document_name = ""
    st.session_state.model_selection = MODEL_WITHOUT_NOTES
    st.session_state.upload_widget_version += 1


def clear_api_key_override() -> None:
    st.session_state.groq_api_key_override = ""


def extract_follow_up(answer: str) -> str:
    lines = [line.strip() for line in answer.splitlines() if "?" in line]
    if lines:
        follow_up = re.sub(r"[*_`#>-]", "", lines[-1]).strip()
    else:
        sentences = re.findall(r"[^.!?\n]*\?", answer)
        if not sentences:
            return "Would you like an example or a short practice question?"
        follow_up = re.sub(r"[*_`#>-]", "", sentences[-1]).strip()
    return " ".join(follow_up.split())[:180]


def hide_follow_up_from_answer(answer: str, follow_up: str) -> str:
    if not follow_up:
        return answer
    lines = answer.splitlines()
    for index in range(len(lines) - 1, -1, -1):
        if "?" not in lines[index]:
            continue
        candidate = re.sub(r"[*_`#>-]", "", lines[index]).strip()
        if " ".join(candidate.split()) == follow_up:
            lines[index] = ""
            return "\n".join(lines).rstrip()
    return answer


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    configured_api_key = get_api_key()
    api_key_override = st.text_input(
        "Groq API key (optional override)",
        type="password",
        key="groq_api_key_override",
        help="Use another Groq key for this session without changing your app configuration.",
    ).strip()
    api_key = api_key_override or configured_api_key
    if api_key_override:
        st.caption("Using the sidebar key for this session.")
        st.button("Use configured key", on_click=clear_api_key_override, use_container_width=True)
    elif not configured_api_key:
        st.caption("Enter a Groq key above, or set GROQ_API_KEY in your .env file or app secrets.")

    upload_key = f"notes_upload_{st.session_state.upload_widget_version}"
    upload = st.session_state.get(upload_key)
    model_options = MODEL_OPTIONS_WITH_NOTES if upload is not None else MODEL_OPTIONS_WITHOUT_NOTES
    if st.session_state.model_selection not in model_options:
        st.session_state.model_selection = MODEL_WITHOUT_NOTES

    st.subheader("🤖 Model selection")
    model = st.selectbox(
        "Choose a model",
        options=model_options,
        key="model_selection",
        format_func=lambda model_id: (
            "GPT-OSS 20B · openai/gpt-oss-20b"
            if model_id == MODEL_DEFAULT
            else "Qwen 3.8 27B · qwen/qwen3.8-27b"
            if model_id == MODEL_WITH_NOTES
            else "GPT-OSS 120B · openai/gpt-oss-120b"
        ),
    )
    st.divider()
    st.subheader("📚 Study notes")
    upload = st.file_uploader(
        "Upload PDF, TXT, or DOCX ",
        type=["pdf", "txt", "docx"],
        key=upload_key,
        on_change=sync_model_with_upload,
        args=(upload_key,),
    )
    if upload and st.button("Load notes", use_container_width=True):
        try:
            extracted = read_notes(upload)
            if not extracted.strip():
                st.warning("No readable text found. Scanned PDFs need OCR first.")
            else:
                st.session_state.document_text = extracted
                st.session_state.document_name = upload.name
                st.success("Notes loaded! Mimi will use them everywhere.")
        except Exception as e:
            st.error(f"Could not read file: {e}")
    if st.session_state.document_name:
        st.info(f"Using: {st.session_state.document_name}")
        st.button("Remove notes", use_container_width=True, on_click=remove_notes)
    st.divider()
    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_follow_up = ""
        set_doll("idle", GREETING)
        st.rerun()

notes = st.session_state.document_text


def ready() -> bool:
    if not api_key:
        st.warning("Please add your API key in the sidebar first 🔑")
        return False
    return True


def run_ai(thinking_msg, done_msg, fn, *args):
    """Run an AI call while the doll 'thinks'. Returns the result, or None on error."""
    set_doll("thinking", thinking_msg)
    try:
        with st.spinner(thinking_msg):
            result = fn(*args)
    except Exception as e:
        set_doll("idle", "Oops, something went wrong 😢")
        st.error(ai.friendly_error(e))
        return None
    set_doll("happy", done_msg)
    return result


def ask(q: str) -> None:
    st.session_state.pending = q


def mcqs_to_text(title, questions) -> str:
    lines = [title, "=" * len(title), ""]
    for i, q in enumerate(questions, 1):
        lines.append(f"Q{i}. {q['question']}")
        for label, opt in zip("ABCD", q["options"]):
            lines.append(f"   {label}. {opt}")
        lines.append(f"   Answer: {'ABCD'[q['answer_index']]}. {q['options'][q['answer_index']]}")
        if q["explanation"]:
            lines.append(f"   Why: {q['explanation']}")
        lines.append("")
    return "\n".join(lines)


DIFFICULTIES = ["Easy", "Medium", "Hard"]
tab_chat, tab_plan, tab_mcq, tab_quiz = st.tabs(
    [" Chat & Learn", " Study Planner", " MCQ Maker", " Take a Quiz"]
)

# --------------------------------------------------------------------------
# Tab 1 – Chat & explain concepts
# --------------------------------------------------------------------------
with tab_chat:
    chat_col, rail_col = st.columns([2.25, 1], gap="large")

    with chat_col:
        st.markdown("####  Ask Mimi to explain anything")

        if not st.session_state.messages:
            with st.chat_message("assistant", avatar=MIMI_AVATAR):
                st.markdown(
                    "Hi! My name is Mimi and I am here to be a guide on your learning journey."
                )

        for index, m in enumerate(st.session_state.messages):
            with st.chat_message(
                m["role"],
                avatar="🧑‍🎓" if m["role"] == "user" else MIMI_AVATAR,
            ):
                content = m["content"]
                if (
                    index == len(st.session_state.messages) - 1
                    and m["role"] == "assistant"
                    and not st.session_state.pending
                ):
                    content = hide_follow_up_from_answer(content, st.session_state.chat_follow_up)
                st.markdown(content)

        if st.session_state.chat_follow_up and not st.session_state.pending:
            with st.chat_message("assistant", avatar=MIMI_AVATAR):
                st.caption("Follow-up")
                st.button(
                    st.session_state.chat_follow_up,
                    on_click=ask,
                    args=(st.session_state.chat_follow_up,),
                    use_container_width=True,
                )

        with st.form("chat_composer_form", clear_on_submit=True):
            typed = st.text_input(
                "Message Mimi",
                placeholder="Start a chat…",
            )
            send_question = st.form_submit_button("Send", use_container_width=True)

        question = typed.strip() if send_question and typed.strip() else st.session_state.pending
        st.session_state.pending = None

        if question:
            if ready():
                st.session_state.chat_follow_up = ""
                history = list(st.session_state.messages)
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user", avatar="🧑‍🎓"):
                    st.markdown(question)
                with st.chat_message("assistant", avatar=MIMI_AVATAR):
                    set_doll("thinking", "Hmm, let me think… 🤔")
                    answer_slot = st.empty()
                    answer_slot.markdown(
                        '<span class="thinking-dots" aria-label="Mimi is thinking">'
                        '<i></i><i></i><i></i></span>',
                        unsafe_allow_html=True,
                    )
                    try:
                        answer_parts = []
                        for chunk in ai.chat_stream(question, history, api_key, model, notes):
                            answer_parts.append(chunk)
                            answer_slot.markdown("".join(answer_parts))
                        answer = "".join(answer_parts)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.session_state.chat_follow_up = extract_follow_up(answer)
                        set_doll("happy", "Hope that helped! Want a quiz on this next? 🎯")
                        st.rerun()
                    except Exception as e:
                        st.session_state.messages.pop()
                        set_doll("idle", "Oops, something went wrong 😢")
                        st.error(ai.friendly_error(e))

    with rail_col:
        st.markdown('<div class="suggestion-panel">', unsafe_allow_html=True)
        st.markdown('<div class="rail-title">💡 Suggested questions</div>', unsafe_allow_html=True)
        st.markdown('<span class="rail-kicker">POPULAR</span>', unsafe_allow_html=True)
        starters = [
            "Teach me Python loops with examples.",
            "Explain recursion like I'm a beginner.",
            "What is the difference between a list and a tuple?",
        ]
        for q in starters:
            st.button(q, on_click=ask, args=(q,), use_container_width=True)
        st.markdown('<div class="rail-title" style="margin-top:18px;">🎯 Quick practice</div>', unsafe_allow_html=True)
        st.caption("Turn a topic into an MCQ set or an interactive quiz.")
        st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Tab 2 – Study schedule
# --------------------------------------------------------------------------
with tab_plan:
    st.markdown("####  Build my study schedule")
    with st.form("plan_form"):
        c1, c2 = st.columns(2)
        subject = c1.text_input("What do you want to learn?", placeholder="e.g. Python for data science")
        goal = c2.text_input("Your goal", placeholder="e.g. Pass my exam / build a project")
        c3, c4, c5 = st.columns(3)
        days = c3.number_input("Days available", min_value=1, max_value=90, value=7)
        hours = c4.slider("Hours per day", 0.5, 8.0, 2.0, 0.5)
        level = c5.selectbox("Current level", ["Beginner", "Intermediate", "Advanced"])
        c6, c7 = st.columns(2)
        start = c6.date_input("Start date", value=date.today())
        extra = c7.text_input("Anything else? (optional)", placeholder="Weak topics, best study time…")
        go_plan = st.form_submit_button("✨ Create my schedule", use_container_width=True)

    if go_plan:
        if not subject.strip():
            st.warning("Tell me what you want to learn first 😊")
        elif ready():
            result = run_ai(
                "Planning your schedule…",
                "Your plan is ready! You've got this 💪",
                ai.generate_schedule,
                subject, goal, level, int(days), hours, start.isoformat(), extra, api_key, model, notes,
            )
            if result:
                st.session_state.schedule = result

    if st.session_state.schedule:
        with st.container(border=True):
            st.markdown(st.session_state.schedule)
        st.download_button(
            "⬇️ Download schedule (.md)",
            st.session_state.schedule,
            file_name="study_schedule.md",
            mime="text/markdown",
        )

# --------------------------------------------------------------------------
# Tab 3 – MCQ generator (study mode: answers visible on demand)
# --------------------------------------------------------------------------
with tab_mcq:
    st.markdown("#### Generate MCQs on any topic")
    with st.form("mcq_form"):
        c1, c2, c3 = st.columns([3, 1, 1])
        mcq_topic = c1.text_input("Topic", placeholder="e.g. Python loops")
        mcq_n = c2.slider("How many?", 3, 15, 5)
        mcq_diff = c3.selectbox("Difficulty", DIFFICULTIES, index=1)
        go_mcq = st.form_submit_button("📝 Generate MCQs", use_container_width=True)

    if go_mcq:
        if not mcq_topic.strip():
            st.warning("Enter a topic first 😊")
        elif ready():
            qs = run_ai(
                "Writing your questions…",
                f"Here are your MCQs! Try them first, then peek at the answers 😉",
                ai.generate_mcqs,
                mcq_topic, mcq_n, mcq_diff, api_key, model, notes,
            )
            if qs:
                st.session_state.mcqs = qs
                st.session_state.mcq_topic = mcq_topic

    if st.session_state.mcqs:
        for i, q in enumerate(st.session_state.mcqs, 1):
            with st.container(border=True):
                st.markdown(f"**Q{i}. {q['question']}**")
                for label, opt in zip("ABCD", q["options"]):
                    st.markdown(f"- **{label}.** {opt}")
                with st.expander("Show answer"):
                    right = q["answer_index"]
                    st.success(f"Correct answer: {'ABCD'[right]}. {q['options'][right]}")
                    if q["explanation"]:
                        st.write(q["explanation"])

        b1, b2 = st.columns(2)
        b1.download_button(
            "⬇️ Download MCQs (.txt)",
            mcqs_to_text(f"MCQs: {st.session_state.mcq_topic}", st.session_state.mcqs),
            file_name="mcqs.txt",
            use_container_width=True,
        )
        if b2.button("🎯 Turn these into a quiz", use_container_width=True):
            st.session_state.quiz = {
                "id": uuid.uuid4().hex[:8],
                "topic": st.session_state.mcq_topic,
                "questions": st.session_state.mcqs,
                "submitted": False,
                "answers": [],
            }
            st.success("Quiz ready! Open the 🎯 Take a Quiz tab.")

# --------------------------------------------------------------------------
# Tab 4 – Interactive quiz with scoring
# --------------------------------------------------------------------------
with tab_quiz:
    st.markdown("####  Test yourself")
    quiz = st.session_state.quiz

    with st.expander(" Quiz settings", expanded=quiz is None):
        with st.form("quiz_setup"):
            c1, c2, c3 = st.columns([3, 1, 1])
            quiz_topic = c1.text_input("Quiz topic", placeholder="e.g. Python loops")
            quiz_n = c2.slider("Questions", 3, 15, 5)
            quiz_diff = c3.selectbox("Level", DIFFICULTIES, index=1)
            go_quiz = st.form_submit_button("🚀 Start new quiz", use_container_width=True)

    if go_quiz:
        if not quiz_topic.strip():
            st.warning("Enter a topic first 😊")
        elif ready():
            qs = run_ai(
                "Setting up your quiz…",
                "Quiz time! Take your time and do your best 🌟",
                ai.generate_mcqs,
                quiz_topic, quiz_n, quiz_diff, api_key, model, notes,
            )
            if qs:
                st.session_state.quiz = quiz = {
                    "id": uuid.uuid4().hex[:8],
                    "topic": quiz_topic,
                    "questions": qs,
                    "submitted": False,
                    "answers": [],
                }

    if quiz and not quiz["submitted"]:
        st.markdown(f"**Topic:** {quiz['topic']}  ·  **{len(quiz['questions'])} questions**")
        with st.form(f"quiz_form_{quiz['id']}"):
            labelled_all, choices = [], []
            for i, item in enumerate(quiz["questions"]):
                st.markdown(f"**Q{i + 1}. {item['question']}**")
                labelled = [f"{l}. {o}" for l, o in zip("ABCD", item["options"])]
                labelled_all.append(labelled)
                choices.append(
                    st.radio(
                        f"Answer for question {i + 1}",
                        labelled,
                        index=None,
                        key=f"r_{quiz['id']}_{i}",
                        label_visibility="collapsed",
                    )
                )
            done = st.form_submit_button("✅ Submit answers", use_container_width=True)

        if done:
            quiz["answers"] = [
                labelled_all[i].index(c) if c is not None else None for i, c in enumerate(choices)
            ]
            quiz["submitted"] = True
            score = sum(a == q["answer_index"] for a, q in zip(quiz["answers"], quiz["questions"]))
            pct = score / len(quiz["questions"])
            if pct >= 0.8:
                set_doll("happy", f"Superstar! {score}/{len(quiz['questions'])} 🌟")
            elif pct >= 0.5:
                set_doll("happy", f"Nice work! {score}/{len(quiz['questions'])} – a bit more practice! 💪")
            else:
                set_doll("idle", f"{score}/{len(quiz['questions'])} – no worries, let's review together 💖")
            st.rerun()

    elif quiz and quiz["submitted"]:
        total = len(quiz["questions"])
        score = sum(a == q["answer_index"] for a, q in zip(quiz["answers"], quiz["questions"]))
        m1, m2 = st.columns(2)
        m1.metric("Your score", f"{score} / {total}")
        m2.metric("Accuracy", f"{round(100 * score / total)}%")
        st.progress(score / total)
        if score == total:
            st.balloons()

        st.markdown("##### 📖 Review")
        for i, (q, a) in enumerate(zip(quiz["questions"], quiz["answers"]), 1):
            right = q["answer_index"]
            ok = a == right
            with st.container(border=True):
                st.markdown(f"{'✅' if ok else '❌'} **Q{i}. {q['question']}**")
                if a is None:
                    st.write("You skipped this one.")
                elif not ok:
                    st.write(f"Your answer: {'ABCD'[a]}. {q['options'][a]}")
                st.write(f"Correct answer: **{'ABCD'[right]}. {q['options'][right]}**")
                if q["explanation"]:
                    st.caption(q["explanation"])

        r1, r2 = st.columns(2)
        if r1.button("🔁 Retake this quiz", use_container_width=True):
            st.session_state.quiz = {**quiz, "id": uuid.uuid4().hex[:8], "submitted": False, "answers": []}
            set_doll("idle", "Let's try again – you can do it! 💪")
            st.rerun()
        if r2.button("🆕 New topic", use_container_width=True):
            st.session_state.quiz = None
            set_doll("idle", GREETING)
            st.rerun()

st.divider()
st.caption("💡 Study support only — always verify important details with your course materials or instructor.")
