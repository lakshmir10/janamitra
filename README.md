# 🗳️ JanaMitra (ಜನಮಿತ್ರ) — AI Election Education Assistant

> **"Friend of the People"** — Making democratic processes accessible in any language  
> **PromptWars: Virtual** | Google Antigravity | **7 Google Services**  
> **Live Demo:** [CLOUD_RUN_URL]

---

## 📋 Challenge Vertical: Election Process Education

---

## 🎯 Approach & Logic

### The Problem
950 million voters in India. 22 official languages. Most election education is in English, buried in government PDFs, and never interactive. First-time voters in rural Karnataka can't access the same civic knowledge as English-speaking urban graduates. This isn't just India — it's a global pattern.

### The Solution
JanaMitra is a **country-aware, multilingual AI election educator** that adapts to the user's context from the first interaction:

1. **Country-first onboarding** — User picks their country; all responses, quiz questions, and quick-start suggestions tailor to that country's specific electoral system
2. **7 Google services** working in concert — not checkbox integration, but services that solve real accessibility barriers
3. **Language + Audio** — Translate to 16 languages, listen in any language via TTS
4. **Adaptive learning** — Dynamic quizzes that scale difficulty and focus on the user's country

### Why "Country-First" Matters
A user in India asking "How do I register to vote?" needs to hear about Voter ID cards and the NVSP portal — not about US DMV registration. By selecting country at onboarding, Gemini receives a **country-specific system prompt** with the correct electoral system, election body, terminology, and voting age. This is the core architectural decision that makes JanaMitra genuinely useful rather than generically educational.

---

## 🛠️ Architecture

```
┌──────────────────────────────────────────────┐
│                   USER                        │
│    1. Picks country → tailors everything      │
│    2. Asks question → gets contextual answer  │
│    3. Translates / Listens / Watches / Quizzes│
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│            GOOGLE CLOUD RUN (#2)              │
│  ┌────────────────────────────────────────┐  │
│  │ Flask App                              │  │
│  │                                        │  │
│  │ Country Config → System Prompt Builder │  │
│  │ Topic Classifier → Context Enricher   │  │
│  │                                        │  │
│  │ 5-Layer Prompt Engineering:            │  │
│  │  L1: Country-specific system prompt    │  │
│  │  L2: Conversation history              │  │
│  │  L3: Topic classification              │  │
│  │  L4: Google Search enrichment          │  │
│  │  L5: User query                        │  │
│  └────────────────────────────────────────┘  │
└──────────────┬───────────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼          ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│Gemini  ││Search  ││Trans-  ││TTS     ││YouTube │
│2.0 #1  ││API #3  ││late #5 ││#6      ││API #7  │
└────────┘└────────┘└────────┘└────────┘└────────┘
                 + Civic Info API #4
```

### 7 Google Services

| # | Service | What It Does | Accessibility Barrier Solved |
|---|---------|-------------|------------------------------|
| 1 | **Gemini 2.0 Flash** | Country-aware AI responses + quiz gen | Context barrier |
| 2 | **Cloud Run** | Global deployment | Access barrier |
| 3 | **Custom Search** | Real-time election info grounding | Accuracy barrier |
| 4 | **Civic Info API** | US voter data by address | Location barrier |
| 5 | **Cloud Translation** | 16 languages (10 Indian) | Language barrier |
| 6 | **Cloud TTS** | Audio in any language | Literacy barrier |
| 7 | **YouTube Data** | Educational video recommendations | Learning style barrier |

---

## 🚀 Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/janamitra.git
cd janamitra
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"       # Enables Search, Civic, Translate, TTS, YouTube
export GOOGLE_SEARCH_CX="your-cx-id"
python app.py
# → http://localhost:8080
```

### Deploy to Cloud Run
```bash
./deploy.sh YOUR_PROJECT_ID YOUR_GEMINI_KEY YOUR_GOOGLE_API_KEY YOUR_SEARCH_CX
```

---

## 📁 Project Structure

```
janamitra/
├── app.py              # Flask + 7 Google services + country-aware prompting
├── templates/
│   └── index.html      # Dashboard: onboarding, chat, translate, TTS, video, quiz, theme toggle
├── Dockerfile          # Cloud Run container
├── requirements.txt    # 4 dependencies
├── deploy.sh           # One-command deploy (enables all 7 APIs)
├── BLOG.md             # Build-in-public narrative
├── .gitignore
├── .dockerignore
└── README.md
```

---

## 🧠 Prompting Logic

### Country-Aware System Prompt
When the user selects India, Gemini receives:
```
THE USER'S COUNTRY: India
THEIR ELECTORAL SYSTEM: Parliamentary democracy with FPTP using EVMs and VVPAT
THEIR ELECTION BODY: Election Commission of India (ECI)
VOTING AGE: 18

Tailor ALL responses to India's specific election system, laws, and processes...
```

This means "How do I register?" produces Voter ID + NVSP instructions (India), not DMV registration (US).

### 5-Layer Context Builder
Each query is enriched before hitting Gemini:
1. **System prompt** — country-specific persona + safety guardrails
2. **History** — last 5 exchanges for conversational continuity
3. **Topic** — keyword-scored classification into 6 categories
4. **Search** — Google Custom Search results as grounding context
5. **Query** — the user's actual question

---

## ✅ Evaluation Criteria

| Criteria | Implementation |
|----------|---------------|
| **Code Quality** | Clean Flask architecture, modular functions, single-responsibility helpers |
| **Security** | Env-var secrets, non-partisan guardrails, Gemini safety settings, no PII storage |
| **Efficiency** | 4 dependencies, ~100KB total, graceful degradation per service |
| **Testing** | `/health` with per-service status, fallback quiz data, error handling on all APIs |
| **Accessibility** | Dark/light theme, TTS audio, 16-language translation, ARIA labels, responsive mobile |
| **Google Services** | **7 services** — each solving a specific accessibility barrier |

---

## 📝 License
MIT — Built for PromptWars: Virtual
