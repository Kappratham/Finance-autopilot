# 💰 Finance Autopilot

AI-powered personal finance analysis. Upload any Indian or US bank statement PDF and get instant categorized transactions, spending insights, anomaly detection, and a plain English monthly report.

> Built with FastAPI + Groq (LLaMA-3) + React Native Web. Designed for mobile-first expansion.

---

## Features

- **AI PDF Parser** — works with any bank, no hardcoded rules
- **Auto Categorization** — 9 spending categories labeled by LLM
- **Monthly Report** — plain English summary with actionable suggestions *(Phase 2)*
- **Anomaly Detection** — flags unusual spending *(Phase 2)*
- **RAG Chat** — ask questions about your own finances *(Phase 2)*
- **Multi-currency** — INR (₹) and USD ($) support

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI + Python |
| AI / LLM | Groq API (LLaMA-3 70B) |
| PDF Parsing | PyMuPDF |
| Vector Store | ChromaDB *(Phase 2)* |
| Frontend | React Native Web / Expo *(Phase 3)* |
| Deployment | Railway (backend) + Vercel (frontend) |

---

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/kappratham/finance-autopilot
cd finance-autopilot
```

### 2. Set up backend
```bash
cd backend
pip install -r requirements.txt
```

### 3. Add your Groq API key
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
# Get a free key at https://console.groq.com
```

### 4. Run the server
```bash
uvicorn main:app --reload --port 8000
```

### 5. Open API docs
```
http://localhost:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload` | Upload bank statement PDF |
| POST | `/api/v1/transactions/summary` | Get category breakdown |
| POST | `/api/v1/transactions/by-category` | Filter by category |
| POST | `/api/v1/report/generate` | Generate monthly report *(Phase 2)* |
| POST | `/api/v1/chat` | Chat with your finances *(Phase 2)* |
| POST | `/api/v1/anomaly/detect` | Detect unusual spending *(Phase 2)* |

---

## Project Structure

```
finance-autopilot/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── routers/
│   │   ├── upload.py            # PDF upload + parsing
│   │   └── transactions.py      # Transaction queries
│   ├── services/
│   │   ├── llm.py               # Groq wrapper (swappable)
│   │   ├── parser.py            # AI PDF parser
│   │   └── categorizer.py       # LLM category labeling
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   ├── .env.example
│   └── requirements.txt
└── README.md
```

---

## Swapping LLM Provider

The LLM layer is fully abstracted. To switch from Groq to OpenAI:

```python
# services/llm.py — change only these lines
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o"
```

Nothing else in the codebase changes.

---

## Roadmap

- [x] Phase 1 — PDF parsing + categorization
- [ ] Phase 2 — Report generation + anomaly detection + RAG chat
- [ ] Phase 3 — React Native Web frontend + Railway/Vercel deployment
- [ ] Phase 4 — Auth + persistent storage + mobile app

---

Built by [Pratham Kapure](https://github.com/kappratham)

---

## Frontend Setup (Phase 3)

### Install dependencies
```bash
cd frontend
npm install
```

### Run on web
```bash
npx expo start --web
```

### Run on mobile (after backend is deployed)
```bash
npx expo start
# Scan QR code with Expo Go app
```

### Update API URL
Edit `frontend/.env`:
```
EXPO_PUBLIC_API_URL=http://localhost:8000       # local
EXPO_PUBLIC_API_URL=https://your-app.railway.app  # production
```

---

## Deployment (Railway + Vercel)

### Backend → Railway
1. Push repo to GitHub
2. Go to railway.app → New Project → Deploy from GitHub
3. Select the `backend` folder as root
4. Add environment variable: `GROQ_API_KEY=your_key`
5. Railway auto-detects the Dockerfile and deploys

### Frontend → Vercel
1. Go to vercel.com → New Project → Import from GitHub
2. Set root directory to `frontend`
3. Add environment variable: `EXPO_PUBLIC_API_URL=https://your-railway-app.railway.app`
4. Deploy

