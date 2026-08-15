"""
Buddy — by Kunal
Internship Project

Run it with:
    streamlit run app.py

Streamlit starts a local web server and automatically opens your default
browser to it.
"""

import os
from dotenv import load_dotenv

load_dotenv()
import random
import datetime

import streamlit as st
from groq import Groq

# ---------------------------------------------------------------------------
# Page config (must be the first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Buddy — by Kunal", page_icon="🤖", layout="centered")

 # ---------------------------------------------------------------------------
# AI client
# ---------------------------------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ_API_KEY not found. Please create a .env file and add your API key.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are Buddy, a helpful, friendly AI assistant. Always give a real, "
    "direct, useful answer to the user's message. Never reply with vague "
    "filler like 'I'm ready to help, what do you want to talk about?' — "
    "if the message is short or ambiguous, make your best reasonable "
    "interpretation and answer that, rather than asking what they meant."
)

STARTER_PROMPTS = [
    "What is Python?",
    "Tell me a joke",
    "What's the time?",
]

# ---------------------------------------------------------------------------
# Session state — persists chat history, bot name, etc. across Streamlit's
# reruns (Streamlit re-executes this whole script on every interaction).
# ---------------------------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []
if "bot_name" not in st.session_state:
    st.session_state.bot_name = "Buddy"
if "awaiting_rename" not in st.session_state:
    st.session_state.awaiting_rename = False
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None


# ---------------------------------------------------------------------------
# Reply logic — rule-based first, Groq LLM as fallback, with conversation
# context so follow-ups like "explain shorter" actually work.
# ---------------------------------------------------------------------------

def rule_based_reply(text):
    bot_name = st.session_state.bot_name
    words = text.split()

    if words and words[0] in ["hi", "hello", "hey", "yo", "hiya"] and len(words) <= 3:
        return random.choice([
            f"Hey there! I'm {bot_name} 👋 What can I help you with?",
            "Hello! 😊 Ask me anything — I'm all ears.",
            f"Hi! {bot_name} here. What's on your mind?",
        ])

    if any(w in text for w in ["bye", "exit", "quit", "goodbye", "see you"]):
        return f"Goodbye! Have a great day! 😊 - {bot_name}"

    if any(w in text for w in ["change name", "rename", "change your name", "new name"]):
        return "CHANGE_NAME"

    if "time" in text and any(d in text for d in ["date", "today"]):
        now = datetime.datetime.now()
        return f"📅 {now.strftime('%d %B %Y')}   ⏰ {now.strftime('%H:%M:%S')}"

    if any(w in text for w in ["time", "what time"]):
        return f"It's ⏰ {datetime.datetime.now().strftime('%H:%M:%S')} right now."

    if any(w in text for w in ["date", "today", "what day", "which date"]):
        return f"Today is 📅 {datetime.datetime.now().strftime('%A, %d %B %Y')}"

    if any(w in text for w in ["sad", "upset", "depressed", "hurt", "lonely", "stressed", "cry"]):
        return random.choice([
            "I'm sorry you're feeling that way 😔 Want to talk about it?",
            "Hey, it's okay to feel like this sometimes. Better days are coming 💪",
            f"I'm here for you, always. What's on your mind? - {bot_name}",
        ])

    if any(w in text for w in ["happy", "awesome", "excited", "wonderful", "amazing"]):
        return random.choice([
            "That's great to hear! Keep that energy up 😊",
            "Love that for you! 🎉",
            "Nice! Hold onto that feeling ✨",
        ])

    for phrase in ["my name is", "i am", "call me", "i'm"]:
        if phrase in text:
            user_name = text.split(phrase)[-1].strip().title()
            return f"Nice to meet you, {user_name}! 😊" if user_name else "What should I call you?"

    if any(w in text for w in ["your name", "who are you", "introduce yourself"]):
        return f"I'm {bot_name} — your AI assistant. 🤖"

    if any(w in text for w in ["joke", "funny", "make me laugh"]):
        return random.choice([
            "Why do programmers prefer dark mode?\nBecause light attracts bugs. 🐛",
            "Why did the Python dev wear glasses?\nBecause they couldn't C#. 😂",
            "I asked my computer for a break...\nnow it keeps sending me Kit-Kat ads. 🍫",
            "Why is 6 afraid of 7?\nBecause 7 8 9. 😄",
        ])

    if words and words[0] in ["ok", "okay", "hmm", "yep", "yup"] and len(words) <= 2:
        return random.choice([
            "Go ahead, I'm listening 👂",
            "Sure, what do you need? 😊",
            f"{bot_name} is ready when you are 🤖",
        ])

    return None

def build_conversation_messages(new_text, max_turns=6):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    recent = st.session_state.history[-max_turns:]
    for turn in recent:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["bot"]})
    messages.append({"role": "user", "content": new_text})
    return messages


def ai_reply(messages):
    try:
        result = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
        )
        return result.choices[0].message.content

    except Exception as err:
        st.error(f"❌ AI Error: {err}")
        print(err)
        return f"Error: {err}"
 
def transcribe_audio(audio_bytes):
    try:
        result = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=("voice.wav", audio_bytes),
        )
        return result.text
    except Exception as err:
        print("Transcription failed:", err)
        return None


def handle_message(text):
    text_stripped = text.strip()
    if not text_stripped:
        return

    if st.session_state.awaiting_rename:
        st.session_state.awaiting_rename = False
        old_name = st.session_state.bot_name
        st.session_state.bot_name = text_stripped.title()
        reply = f"Done — you can call me {st.session_state.bot_name} now instead of {old_name}! 🎉"
        _log(text_stripped, reply)
        return

    lowered = text_stripped.lower()
    with st.spinner(f"{st.session_state.bot_name} is thinking..."):
        reply = rule_based_reply(lowered)
        if reply is None:
            messages = build_conversation_messages(text_stripped)
            reply = ai_reply(messages)

    if reply == "CHANGE_NAME":
        st.session_state.awaiting_rename = True
        reply = "Sure — what should I go by? 😊"

    _log(text_stripped, reply)


def _log(user_text, bot_text):
    now = datetime.datetime.now()
    st.session_state.history.append({
        "user": user_text,
        "bot": bot_text,
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%d %B %Y"),
    })


# ---------------------------------------------------------------------------
# Styling — "aurora console": a drifting three-color gradient backdrop
# behind a frosted glass chat panel. The avatar orb is cut from the same
# gradient as the backdrop, tying the bot's identity to the world behind it.
# ---------------------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root{
  --void:#06070c; --ink:#0d0f1a; --glass:rgba(20,22,36,0.55);
  --border:rgba(255,255,255,0.08); --border-strong:rgba(255,255,255,0.16);
  --iris:#8b7cf6; --ember:#ff9166; --teal:#4fd1c5;
  --paper:#f5f6fb; --mist:#a6adc3; --mist-dim:#6b7284;
  --gradient: linear-gradient(135deg, var(--iris) 0%, #b06cf6 40%, var(--ember) 75%, var(--teal) 100%);
}

html, body, .stApp{ background:var(--void); }

/* drifting aurora backdrop */
.stApp::before{
  content:""; position:fixed; inset:-20%; z-index:0; pointer-events:none;
  background:
    radial-gradient(38% 30% at 20% 20%, rgba(139,124,246,0.30), transparent 70%),
    radial-gradient(34% 28% at 85% 15%, rgba(255,145,102,0.22), transparent 70%),
    radial-gradient(40% 32% at 60% 85%, rgba(79,209,197,0.18), transparent 70%);
  filter: blur(60px);
  animation: drift 22s ease-in-out infinite alternate;
}
@keyframes drift{
  0%{ transform: translate(0,0) rotate(0deg); }
  100%{ transform: translate(-3%, 4%) rotate(6deg); }
}

.block-container{ position:relative; z-index:1; padding-top:2.2rem; max-width:640px; }

/* glass console card wrapping the header */
.console{
  background:var(--glass); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
  border:1px solid var(--border); border-radius:20px;
  padding:18px 20px; margin-bottom:20px;
  box-shadow: 0 20px 60px -25px rgba(0,0,0,0.6);
}

.buddy-header{ display:flex; align-items:center; gap:14px; }
.buddy-orb-wrap{ position:relative; width:50px; height:50px; flex-shrink:0; }
.buddy-orb{
  width:50px; height:50px; border-radius:50%; background:var(--gradient);
  background-size:220% 220%;
  display:flex; align-items:center; justify-content:center; font-size:21px;
  animation: breathe 3.4s ease-in-out infinite, hue 8s ease-in-out infinite;
  box-shadow: 0 0 24px -4px rgba(139,124,246,0.65);
}
@keyframes breathe{ 0%,100%{ transform:scale(1); } 50%{ transform:scale(1.08); } }
@keyframes hue{ 0%,100%{ background-position:0% 50%; } 50%{ background-position:100% 50%; } }

.buddy-title{
  font-family:'Space Grotesk', sans-serif; font-weight:700; font-size:21px;
  background:var(--gradient); background-size:220% 220%;
  -webkit-background-clip:text; background-clip:text; color:transparent;
  animation: hue 8s ease-in-out infinite;
}
.buddy-status{ display:flex; align-items:center; gap:6px; margin-top:3px; }
.buddy-dot{ width:6px; height:6px; border-radius:50%; background:#3ddc97; box-shadow:0 0 6px #3ddc97; }
.buddy-status span{ font-size:12px; color:var(--mist-dim); font-family:'JetBrains Mono', monospace; }
.buddy-credit{ font-size:11px; color:var(--mist-dim); font-family:'JetBrains Mono', monospace; margin-left:auto; text-align:right; opacity:0.8; }

/* chat messages */
.msg-row{ display:flex; margin-bottom:14px; position:relative; z-index:1; }
.msg-row.user{ justify-content:flex-end; }
.msg-row.bot{ justify-content:flex-start; }
.msg-col{ max-width:80%; display:flex; flex-direction:column; }
.msg-sender{ font-size:10.5px; font-family:'JetBrains Mono', monospace; color:var(--mist-dim); margin-bottom:4px; padding:0 6px; letter-spacing:0.3px; }
.msg-row.user .msg-sender{ text-align:right; }

.bubble{
  padding:12px 16px; border-radius:18px; font-size:14.5px; line-height:1.6;
  white-space:pre-wrap; word-wrap:break-word;
  transition: transform .15s ease, box-shadow .15s ease;
}
.msg-row.bot .bubble{
  background:var(--glass); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border:1px solid var(--border); color:var(--paper); border-bottom-left-radius:5px;
}
.msg-row.bot .bubble:hover{ border-color:var(--border-strong); transform:translateY(-1px); }
.msg-row.user .bubble{
  background:var(--gradient); background-size:180% 180%; color:#100c1e; font-weight:500;
  border-bottom-right-radius:5px; box-shadow:0 8px 24px -10px rgba(139,124,246,0.55);
}
.msg-row.user .bubble:hover{ transform:translateY(-1px); box-shadow:0 12px 28px -10px rgba(139,124,246,0.7); }

/* empty-state hero */
.hero{ text-align:center; padding:38px 10px 26px 10px; position:relative; z-index:1; }
.hero-orb{
  width:64px; height:64px; margin:0 auto 16px auto; border-radius:50%;
  background:var(--gradient); background-size:220% 220%;
  animation: breathe 3.4s ease-in-out infinite, hue 8s ease-in-out infinite;
  box-shadow: 0 0 40px -6px rgba(139,124,246,0.6);
  display:flex; align-items:center; justify-content:center; font-size:28px;
}
.hero h2{ font-family:'Space Grotesk', sans-serif; color:var(--paper); font-weight:700; margin:0 0 6px 0; }
.hero p{ color:var(--mist); font-size:14px; margin:0; }

/* suggestion chips (Streamlit buttons re-themed) */
div[data-testid="stHorizontalBlock"] .stButton button{
  background:var(--glass) !important; color:var(--paper) !important;
  border:1px solid var(--border) !important; border-radius:999px !important;
  font-family:'Inter', sans-serif !important; font-size:13px !important;
  padding:8px 16px !important; transition:all .15s ease !important;
}
div[data-testid="stHorizontalBlock"] .stButton button:hover{
  border-color:var(--iris) !important; color:var(--iris) !important; transform:translateY(-1px);
}

/* sidebar */
section[data-testid="stSidebar"]{ background:var(--ink); border-right:1px solid var(--border); }
section[data-testid="stSidebar"] *{ color:var(--paper); }
section[data-testid="stSidebar"] .stButton button{
  background:var(--glass) !important; border:1px solid var(--border) !important;
  border-radius:12px !important; transition:all .15s ease !important;
}
section[data-testid="stSidebar"] .stButton button:hover{ border-color:var(--iris) !important; }

/* chat input */
.stChatInput{ position:relative; z-index:1; }
.stChatInput textarea, .stChatInput input{
  background:var(--glass) !important; color:var(--paper) !important;
  border:1px solid var(--border) !important; border-radius:16px !important;
  backdrop-filter: blur(14px) !important;
}
.stChatInput textarea:focus, .stChatInput input:focus{
  border-color:var(--iris) !important; box-shadow:0 0 0 3px rgba(139,124,246,0.18) !important;
}

::-webkit-scrollbar{ width:8px; }
::-webkit-scrollbar-thumb{ background:var(--border-strong); border-radius:8px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ⚙️ Controls")

    new_name = st.text_input("Rename Buddy", value=st.session_state.bot_name)
    if new_name and new_name != st.session_state.bot_name:
        st.session_state.bot_name = new_name.strip().title()
        st.rerun()

    st.divider()

    st.markdown("### 🎙️ Voice input")
    audio = st.audio_input("Record a message")
    if audio is not None:
        audio_id = hash(audio.getvalue())
        if audio_id != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio_id
            with st.spinner("Transcribing..."):
                transcript = transcribe_audio(audio.getvalue())
            if transcript:
                handle_message(transcript)
                st.rerun()
            else:
                st.warning("Couldn't transcribe that — try again.")

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.caption("Buddy — by Kunal\nInternship Project · Hybrid rule-based + LLaMA (Groq)")


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(f"""
<div class="console">
  <div class="buddy-header">
    <div class="buddy-orb-wrap"><div class="buddy-orb">🤖</div></div>
    <div>
      <div class="buddy-title">{st.session_state.bot_name}</div>
      <div class="buddy-status"><div class="buddy-dot"></div><span>online</span></div>
    </div>
    <div class="buddy-credit">Buddy — by Kunal<br>Internship Project</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Chat history / empty-state hero with quick-start chips
# ---------------------------------------------------------------------------

if not st.session_state.history:
    st.markdown(f"""
    <div class="hero">
      <div class="hero-orb">👋</div>
      <h2>Hey! I'm {st.session_state.bot_name}</h2>
      <p>Ask me anything, or try one of these to get started</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(STARTER_PROMPTS))
    for col, prompt in zip(cols, STARTER_PROMPTS):
        with col:
            if st.button(prompt, use_container_width=True, key=f"chip_{prompt}"):
                handle_message(prompt)
                st.rerun()

for chat in st.session_state.history:
    st.markdown(f"""
    <div class="msg-row user"><div class="msg-col">
      <div class="msg-sender">You</div>
      <div class="bubble">{chat['user']}</div>
    </div></div>
    <div class="msg-row bot"><div class="msg-col">
      <div class="msg-sender">{st.session_state.bot_name}</div>
      <div class="bubble">{chat['bot']}</div>
    </div></div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

user_text = st.chat_input("Type a message...")
if user_text:
    handle_message(user_text)
    st.rerun()
