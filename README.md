# 📚 StudyBuddy AI – Your Personal AI Learning Assistant

StudyBuddy AI is an AI-powered learning assistant designed to make studying easier, smarter, and more interactive. It helps students understand concepts, create personalized study schedules, generate multiple-choice questions, and test their knowledge through interactive quizzes.

Meet **Mimi**, your friendly AI study buddy, who guides you throughout your learning journey!

🚀 **Live Demo:** https://study-buddy-ai-chatbot.streamlit.app/

💻 **GitHub Repository:** https://github.com/Hemi26-gif/study-buddy-ai-chatbot

---

## ✨ Features

### 1. 💬 AI Chat & Learn
- Ask questions on different subjects and topics.
- Get simple, step-by-step explanations.
- Receive practical examples and code explanations.
- Continue conversations with chat history.
- Get answers based on uploaded study materials.

### 2. 📅 Personalized Study Planner
- Generate customized study schedules.
- Set learning goals and current knowledge levels.
- Choose the number of study days and hours per day.
- Receive daily learning tasks and revision schedules.
- Get a structured plan based on your requirements.

### 3. 📝 MCQ Generator
- Generate multiple-choice questions on any topic.
- Choose the number of questions.
- Select difficulty levels: Easy, Medium, and Hard.
- View correct answers with explanations.
- Download generated MCQs as a text file.

### 4. 🎯 Interactive Quiz
- Take quizzes based on your selected topics.
- Answer multiple-choice questions.
- Submit answers and receive instant scores.
- View accuracy and correct answers.
- Review explanations and retake quizzes.

### 5. 📂 Upload Study Materials
- Upload PDF, TXT, and DOCX files.
- Extract text from study materials.
- Use uploaded notes as context for AI-generated responses.
- Get explanations and learning support based on your documents.

### 6. 🤖 AI-Powered Learning
- Powered by Groq LLM integration.
- Uses LangChain for AI prompt management and conversation handling.
- Supports model selection.
- Provides a friendly learning experience through Mimi.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| LangChain | LLM integration and prompt management |
| Groq API | AI-powered responses and content generation |
| GPT-OSS / Qwen | Supported AI language models |
| PyPDF | PDF text extraction |
| Python-docx | DOCX document processing |
| Python-dotenv | Environment variable management |

---

## 📁 Project Structure

```text
study-buddy-ai-chatbot/
│
├── assets/
│   └── Application images and resources
│
├── app.py
│   └── Main Streamlit application
│
├── ai_engine.py
│   └── AI logic, prompts and model integration
│
├── ui_theme.py
│   └── Application UI styling and theme
│
├── requirements.txt
│   └── Project dependencies
│
├── .env
│   └── API key configuration (create locally)
│
└── README.md
    └── Project documentation
```

---

## ⚙️ Installation & Setup

Follow these steps to run StudyBuddy AI locally.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Hemi26-gif/study-buddy-ai-chatbot.git
```

### Step 2: Navigate to the Project Folder

```bash
cd study-buddy-ai-chatbot
```

### Step 3: Create a Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate the environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Groq API Key

Get your API key from:

https://console.groq.com/

Create a `.env` file in the project root and add:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Alternatively, enter your API key directly in the application's sidebar.

**Important:** Never upload your API key or `.env` file to GitHub.

### Step 6: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser, usually at:

```text
http://localhost:8501
```

---

## 🚀 Live Application

Try StudyBuddy AI here:

👉 https://study-buddy-ai-chatbot.streamlit.app/

Explore its AI chat, personalized study planner, MCQ generator, and interactive quiz features.

---

## 🎯 Project Objective

The main objective of StudyBuddy AI is to create a personalized learning environment where students can access learning support in one place.

Instead of using separate tools for understanding concepts, preparing study schedules, generating practice questions, and evaluating knowledge, students can use one AI-powered platform to support their learning journey.

---

## 🔮 Future Enhancements

- Add user authentication and personalized profiles.
- Save and track individual learning progress.
- Introduce performance analytics and progress dashboards.
- Support additional document formats.
- Add multilingual learning support.
- Provide personalized recommendations based on quiz performance.

---

## 👩‍💻 Author

**Developed by: Hemitha Ilan**

GitHub: https://github.com/Hemi26-gif

---

⭐ If you find this project useful, consider giving the repository a star!

**Study Smart. Learn Better. Grow Faster with StudyBuddy AI!**
