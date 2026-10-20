# 🗣️ VerbaFlow AI · English Speaking & Fluency Coach

An interactive, voice-first AI English speaking partner and fluency coach. Practice real-world conversations, master business interviews, and receive **real-time grammar corrections, native alternatives, and vocabulary boosters**.

---

## ✨ Features

- **💼 Category A: Business & Career Scenarios**
  - Job Interview (*"Tell me about yourself"*, handling challenges, behavioral questions)
  - Project Pitching & Q&A
  - Client Negotiation & Polite Disagreement
- **☕ Category B: Daily Life & Fluency**
  - Coffee Shop & Restaurant Ordering (customizing drinks, asking recommendations)
  - Airport Check-in & Immigration Questions
  - Casual Weekend Small Talk
- **🎯 Category C: Real-Time Grammar & Native Polish**
  - **Live Grammar Diff:** Highlights mistakes and shows the correct grammatical form.
  - **Bilingual Explanations:** Clear Thai & English explanations of grammar rules.
  - **Native Phrasing Alternatives:** Casual vs. Formal ways native speakers express the same thought.
  - **Vocab & Idiom Booster:** Automatically suggests idioms and phrasal verbs.
- **🔊 Dual-Voice Architecture**
  - ⚡ **Edge-TTS (100% Free & Unlimited):** High quality US, UK, and Australian native accents (Jenny, Guy, Sonia, Ryan, Natasha) with adjustable speed (0.85x, 1.0x, 1.15x).
  - 💎 **ElevenLabs (Ultra-Realistic Neural):** Powered by `eleven_flash_v2_5` for realistic intonation and low latency.
- **🎙️ Zero-Install Microphone Input:** Leverages browser Web Speech API for real-time speech-to-text with zero lag and native English pronunciation tracking.

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/<your-username>/verbaflow-ai.git
cd verbaflow-ai
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Create a `.env` file or set environment variables:

```bash
# Optional: for ElevenLabs Neural voice
export ELEVENLABS_API_KEY="your-key"

# Optional: for Google Gemini LLM
export GEMINI_API_KEY="your-key"
```

*(Note: Edge-TTS and the built-in ESL grammar rule engine work 100% out of the box with zero API keys!)*

### 3. Launch the Web App

On Windows:
```cmd
run_tutor.bat
```

Or via Python:
```bash
python server.py
```

Then open your browser at **`http://127.0.0.1:8766`**.

---

## 🛠️ Architecture

```
User (Browser Microphone)
       │
       ▼ (Web Speech API - en-US)
[Text Transcript]
       │
       ▼
[Python HTTP Backend (server.py:8766)]
       │
       ├─► [Tutor Engine (tutor_engine.py)]
       │      ├─ Gemini 2.5 Flash / OpenAI / Built-in ESL Rule Engine
       │      └─ Generates: Spoken Reply + Grammar Feedback Card
       │
       └─► [TTS Service (tts_service.py)]
              ├─ Edge-TTS (Free US/UK/AU)
              ├─ ElevenLabs Flash v2.5
              └─ Local Disk Audio Cache
```

---

## 📄 License

MIT License. Open-source for personal learning and educational use.
