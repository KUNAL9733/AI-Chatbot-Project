# 🤖 Buddy — AI Chatbot

Buddy is a hybrid AI chatbot built with **Streamlit**, combining fast rule-based responses for common queries with **Groq's LLaMA 3.3 70B** for open-ended conversation. It also supports **voice input** with automatic transcription, all wrapped in a custom-styled "aurora glass" chat UI.

> Internship Project by **Kunal**

---

## ✨ Features

- **Hybrid response engine** — instant rule-based replies for greetings, farewells, jokes, time/date, mood check-ins, and name changes, with a Groq-powered LLM fallback for everything else
- **Conversational memory** — keeps recent chat turns as context so follow-ups (e.g. "explain shorter") make sense
- **Voice input** — record a message in the sidebar and it's transcribed automatically using Whisper (`whisper-large-v3`)
- **Renameable bot** — rename Buddy on the fly, either via the sidebar or by chatting ("change your name")
- **Custom UI** — animated gradient background, glassmorphism chat bubbles, and quick-start suggestion chips for first-time users
- **Session-based history** — chat log persists across interactions using Streamlit's session state, with a one-click "Clear chat" option

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / App | [Streamlit](https://streamlit.io/) |
| LLM | [Groq](https://groq.com/) — `llama-3.3-70b-versatile` |
| Speech-to-text | Groq — `whisper-large-v3` |
| Language | Python |
| Config | `python-dotenv` |

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit groq python-dotenv
   ```

3. **Set up your API key**

   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   Get a free API key from [Groq Console](https://console.groq.com/).

4. **Run the app**
   ```bash
   streamlit run main.py
   ```
   This starts a local server and opens Buddy in your default browser.

---

## 🗂️ Project Structure

```
.
├── main.py          # App entry point — UI, chat logic, Groq integration
├── .env              # API keys (not committed)
└── README.md
```

---

## 💬 How It Works

1. User sends a message (typed or spoken).
2. Buddy first checks it against a set of **rule-based patterns** (greetings, jokes, time/date, mood, etc.).
3. If no rule matches, the message — along with recent conversation history — is sent to **Groq's LLaMA 3.3 70B** for a generated response.
4. Voice messages are transcribed via **Whisper** before going through the same pipeline.
5. Every exchange is logged to session state and rendered in a styled chat bubble.

---

## 📌 Notes

- Requires a valid `GROQ_API_KEY` to run — the app will show an error and stop without one.
- All chat history is stored in-memory for the session only (not persisted to a database).

---

## 📄 License

This project was built for internship/educational purposes. Feel free to fork and adapt it.
