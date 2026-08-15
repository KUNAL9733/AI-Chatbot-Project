# 🤖 Buddy — by Kunal

An AI-powered desktop-style chatbot, rebuilt as a web app using **Streamlit**.
Built as an internship project.

Buddy uses a **hybrid architecture**: fast keyword-based rules handle common
requests instantly (greetings, jokes, date/time, mood check-ins), and
anything more open-ended is passed to an LLM via the **Groq API** for a
real, intelligent response.

---

## ✨ Features

- 💬 Real-time chat with a hybrid rule-based + LLM engine, with conversation
  memory so follow-ups like "explain that shorter" work correctly
- 🎙️ Voice input — record your voice, transcribed automatically using Groq's
  Whisper model (no external speech libraries needed)
- ✏️ Rename Buddy to anything you like, on the fly
- 🗑️ Clear chat history anytime
- 🎨 **Aurora console UI** — a frosted-glass chat panel floating over a
  slowly drifting three-color gradient backdrop, with quick-start prompt
  chips and hover micro-interactions. Fully custom, not a default
  Streamlit theme.

---

## 🛠️ Tech Stack

| Layer            | Technology                          |
|-------------------|--------------------------------------|
| UI / Web framework | [Streamlit](https://streamlit.io)   |
| AI model           | GPT-OSS 120B (via [Groq](https://groq.com)) |
| Speech-to-text     | Groq Whisper (`whisper-large-v3`)   |
| Language           | Python 3.10+                        |

---

## 📁 Project Structure

```
Buddy/
├── main.py              # Main application (UI + logic)
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── PROJECT_GUIDE.md      # Full setup guide
├── QUICK_REFERENCE.md    # Quick commands
├── .gitignore
└── .env                  # Your local API key (never commit this)
```

---

## 🚀 How to Run

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Add your Groq API key.**
Get a free key at [console.groq.com](https://console.groq.com), then set it
as an environment variable:

- **Windows (PowerShell):**
  ```powershell
  $env:GROQ_API_KEY="your-key-here"
  ```
- **macOS / Linux:**
  ```bash
  export GROQ_API_KEY="your-key-here"
  ```

**3. Run the app:**
```bash
streamlit run main.py
```

Streamlit will start a local server and automatically open Buddy in your
default browser at `http://localhost:8501`.

---

## 🧠 How It Works

1. Streamlit renders the whole script into a web page and reruns it on every
   interaction, using `st.session_state` to persist chat history, the bot's
   name, and other state between reruns.
2. When you send a message, it's first checked against a set of **rule-based
   patterns** (greetings, jokes, time/date, mood responses, etc.) for an
   instant reply.
3. If no rule matches, the message is sent to the **Groq API**, which runs
   it through LLaMA 3.3 70B and returns a generated response.
4. Voice messages are recorded in-browser, sent to Groq's Whisper model for
   transcription, and then run through the exact same reply pipeline as
   typed text.
5. The conversation is stored in memory for the session and cleared with the
   "Clear chat" button in the sidebar whenever you like.

---

## 👤 Author

**Kunal**
Internship Project — Buddy AI Chatbot
