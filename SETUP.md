# Auditor AI — Complete Setup & Run Guide

> Step-by-step instructions to get the **entire project** running from scratch on **Windows**.
> (macOS/Linux users: swap `.\venv\Scripts\activate` with `source venv/bin/activate`)

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Get Your API Keys (Free)](#2-get-your-api-keys-free)
3. [Clone & Configure](#3-clone--configure)
4. [Backend Setup](#4-backend-setup)
5. [Frontend Setup](#5-frontend-setup)
6. [Run the Project](#6-run-the-project)
7. [Using the App](#7-using-the-app)
8. [Docker Deployment (Optional)](#8-docker-deployment-optional)
9. [Render.com Deployment (Optional)](#9-rendercom-deployment-optional)
10. [Project Structure](#10-project-structure)
11. [API Endpoints Reference](#11-api-endpoints-reference)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Prerequisites

Make sure these are installed on your machine before starting:

| Tool | Required Version | Download Link | Check Command |
|------|-----------------|---------------|---------------|
| **Python** | 3.10+ (3.12 recommended) | [python.org/downloads](https://www.python.org/downloads/) | `python --version` |
| **Node.js** | 18+ (LTS) | [nodejs.org](https://nodejs.org/) | `node --version` |
| **npm** | 9+ (comes with Node.js) | — | `npm --version` |
| **Git** | Any | [git-scm.com](https://git-scm.com/) | `git --version` |

> **MongoDB**: You can use either a **local MongoDB** installation or **MongoDB Atlas** (free cloud). Atlas is easier — see Step 2.

---

## 2. Get Your API Keys (Free)

You need **3 API keys** (all have generous free tiers). Here's exactly how to get each one:

### 2a. Google Gemini API Key (AI/LLM)

1. Go to **[https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Select any Google Cloud project (or create one)
5. **Copy the key** — it looks like: `AIzaSy...`

> Free tier: 15 requests/minute, 1 million tokens/day — more than enough for development.

### 2b. Pinecone API Key (Vector Database)

1. Go to **[https://app.pinecone.io](https://app.pinecone.io)**
2. Sign up for a **free Starter account**
3. Once logged in, click **"API Keys"** in the left sidebar
4. **Copy the API key**
5. Now **create an index**:
   - Click **"Indexes"** → **"Create Index"**
   - **Name**: `legal-docs` (or whatever you prefer)
   - **Dimensions**: `384`
   - **Metric**: `cosine`
   - **Cloud**: `AWS` → `us-east-1` (Starter plan)
   - Click **Create**
6. After creation, click the index name → **copy the Host URL**
   - It looks like: `legal-docs-abc123.svc.aped-1234.pinecone.io`

### 2c. MongoDB Atlas (Free Cloud Database)

1. Go to **[https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)**
2. Sign up and create a **free M0 cluster** (Shared tier)
3. Set a **database username** and **password**
4. Under **Network Access** → Click **"Add IP Address"** → Select **"Allow Access from Anywhere"** (for development)
5. Under **Database** → Click **"Connect"** → Choose **"Connect your application"**
6. **Copy the connection string** — it looks like:
   ```
   mongodb+srv://username:password@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
   ```
7. Replace `username` and `password` with the ones you set

### 2d. Redis / Upstash (Optional — For Chat Caching)

> The app works **perfectly without Redis**. This is optional for performance optimization.

1. Go to **[https://upstash.com](https://upstash.com)**
2. Sign up (free tier: 10,000 commands/day)
3. Create a **Redis database** → Region: closest to you
4. Go to **"REST API"** tab → Copy the **Redis URL**
   - It looks like: `redis://default:abc123@us1-xxx.upstash.io:6379`

---

## 3. Clone & Configure

### 3a. Clone the Repository

```powershell
git clone https://github.com/Ani1801/Legal_Document_Summarizer.git
cd Legal_Document_Summarizer
```

### 3b. Create Environment File

```powershell
copy .env.example .env
```

### 3c. Edit the `.env` File

Open `.env` in your code editor and fill in your actual API keys:

```env
# ── Authentication ──
SECRET_KEY=any-random-string-at-least-32-characters-long
ALGORITHM=HS256

# ── MongoDB ──
MONGO_URI=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=legal_document_summarizer

# ── Google Gemini AI ──
GOOGLE_API_KEY=AIzaSy-YOUR-KEY-HERE

# ── Pinecone Vector Database ──
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_INDEX_NAME=legal-docs
PINECONE_HOST=legal-docs-abc123.svc.aped-1234.pinecone.io

# ── Redis / Upstash (Optional) ──
# REDIS_URL=redis://default:your-password@your-host.upstash.io:6379

# ── File Uploads ──
UPLOADS_DIR=uploads
```

> ⚠️ **NEVER** commit `.env` to Git. It is already in `.gitignore`.

---

## 4. Backend Setup

### 4a. Create a Virtual Environment

```powershell
cd backend

# Create venv
python -m venv venv

# Activate it (Windows PowerShell)
.\venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### 4b. Install Dependencies

```powershell
pip install -r requirements.txt
```

> ⏳ **First time takes 3-5 minutes** — it downloads ML models and many packages.
>
> If any package fails, try these individually:
> ```powershell
> pip install langchain-community langchain-huggingface langchain-pinecone langchain-google-genai
> pip install sentence-transformers python-multipart reportlab python-docx redis
> ```

### 4c. Create Uploads Directory

```powershell
mkdir uploads
```

### 4d. Test Backend Imports

```powershell
python -c "from main import app; print('All imports OK!')"
```

If this prints `All imports OK!` — you're ready! If it shows errors, see [Troubleshooting](#12-troubleshooting).

---

## 5. Frontend Setup

Open a **new terminal** (keep the backend terminal open):

```powershell
cd frontend
npm install
```

> ⏳ First time takes 1-2 minutes.

---

## 6. Run the Project

You need **two terminals** running simultaneously:

### Terminal 1 — Backend API Server

```powershell
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
```

### Terminal 2 — Frontend Dev Server

```powershell
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in XXXms
  ➜  Local:   http://localhost:5173/
```

### 🎉 Open Your Browser

Navigate to **http://localhost:5173**

You'll see the landing page. Click **"Get Started Free"** to create an account!

> **Quick Start Alternative**: Just double-click `setup.bat` in the project root to auto-install all dependencies. Then run the two servers manually.

---

## 7. Using the App

### Step 1: Sign Up
- Click "Get Started Free" → Create an account with email & password

### Step 2: Upload a Document
- Go to **"New Summary"** in the sidebar
- Upload any PDF (legal contract, agreement, policy, etc.)
- Wait 15-30 seconds for the AI to analyze it

### Step 3: View Audit Results
- See the **Risk Score**, **Summary**, **Risks**, and **Suggestions**
- Click **"Chat with Doc"** to ask questions about the document
- Click **"Export PDF"** or **"Export DOCX"** to download a branded report

### Step 4: Compare Documents
- Go to **"Compare"** in the sidebar
- Select two previously audited documents
- Click "Compare Documents" to see a side-by-side analysis

### Step 5: Run Compliance Check
- Go to **"Compliance"** in the sidebar
- Select a document and choose regulations (GDPR, CCPA, AI Act)
- Click "Run Compliance Check" to see violations and action items

### Step 6: Dashboard & Library
- **Dashboard**: Overview of all audits, stats, and recent activity
- **Library**: Browse all uploaded documents, open chat for any of them
- **Bell Icon** (top right): See notifications about audit results

---

## 8. Docker Deployment (Optional)

If you have Docker installed, you can run everything with one command:

```powershell
# From the project root
docker-compose up --build
```

This starts:
- **Backend** → `http://localhost:8000`
- **Frontend** → `http://localhost:80`
- **MongoDB** → `localhost:27017`

> Make sure your `.env` file is in the project root before running.

---

## 9. Render.com Deployment (Optional)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml` and create both services
5. Add your environment variables in the Render dashboard
6. Deploy!

> **Important for Render**: Update the `API_URL` in the frontend code from `http://localhost:8000/api` to your Render backend URL.

---

## 10. Project Structure

```
Legal_Document_Summarizer/
├── .env.example               # Template for environment variables
├── .gitignore                 # Git ignore rules
├── SETUP.md                   # This file
├── README.md                  # Project overview
├── setup.bat                  # Windows quick-setup script
├── docker-compose.yml         # Docker orchestration
├── render.yaml                # Render.com deployment config
│
├── backend/
│   ├── Dockerfile             # Backend Docker image
│   ├── main.py                # FastAPI entry point + route registration
│   ├── requirements.txt       # Python dependencies
│   ├── uploads/               # Uploaded PDFs (created at runtime)
│   └── app/
│       ├── api/
│       │   ├── auth.py        # POST /api/auth/signup, /login
│       │   ├── audits.py      # POST /api/audits/upload, GET /file/{id}
│       │   ├── chat.py        # POST /api/chat (RAG + Redis cache)
│       │   ├── compare.py     # POST /api/compare
│       │   ├── compliance.py  # POST /api/compliance/check
│       │   ├── dashboard.py   # GET /api/dashboard/stats, /notifications
│       │   ├── export.py      # GET /api/export/{id}?format=pdf|docx
│       │   └── library.py     # GET /api/library
│       ├── core/
│       │   ├── config.py      # Pydantic settings loader
│       │   └── security.py    # JWT tokens + bcrypt hashing
│       ├── models/
│       │   ├── audit.py       # Audit & Risk models
│       │   ├── chat.py        # ChatRequest/Response models
│       │   ├── compare.py     # CompareRequest/Response models
│       │   ├── compliance.py  # ComplianceRequest/Response models
│       │   ├── library.py     # Library document model
│       │   └── user.py        # User auth models
│       └── services/
│           ├── cache_service.py     # Redis/Upstash with fallback
│           ├── database.py          # MongoDB save operations
│           ├── export_service.py    # PDF/DOCX report generation
│           └── ai/
│               ├── audit_service.py      # Gemini audit analysis
│               ├── chat_service.py       # Gemini RAG chat
│               ├── compare_service.py    # Gemini document comparison
│               ├── compliance_service.py # Gemini compliance checker
│               ├── processor.py          # PDF loading & chunking
│               ├── query_service.py      # Vector retrieval
│               └── vector_store.py       # Pinecone embeddings
│
└── frontend/
    ├── Dockerfile             # Frontend Docker image
    ├── nginx.conf             # Nginx config for production
    ├── package.json           # Node dependencies
    └── src/
        ├── App.jsx            # Routes & layout
        ├── index.css          # Global styles
        ├── components/
        │   ├── ActionItems.jsx    # Action items checklist
        │   ├── ChatPanel.jsx      # Slide-out RAG chat drawer
        │   ├── Header.jsx         # Top bar + notifications
        │   ├── RecentAudits.jsx   # Recent audit cards
        │   ├── Sidebar.jsx        # Navigation sidebar
        │   └── StatCards.jsx      # Dashboard stat cards
        ├── context/
        │   ├── AuthContext.jsx    # Auth state management
        │   └── ThemeContext.jsx   # Dark/light mode
        └── pages/
            ├── AuditNew.jsx       # Upload → Audit → Export → Chat
            ├── Auth.jsx           # Login/Signup
            ├── Compare.jsx        # Multi-document comparison
            ├── Compliance.jsx     # Regulation compliance checker
            ├── Dashboard.jsx      # Stats overview
            ├── Landing.jsx        # Public landing page
            ├── Library.jsx        # Document library + chat
            └── Settings.jsx       # User settings
```

---

## 11. API Endpoints Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/signup` | ❌ | Create new account |
| POST | `/api/auth/login` | ❌ | Login & get JWT token |
| GET | `/api/dashboard/stats` | ✅ | Dashboard statistics |
| GET | `/api/audits/recent` | ✅ | Recent 5 audits |
| POST | `/api/audits/upload` | ✅ | Upload PDF & run AI audit |
| GET | `/api/audits/file/{id}` | ✅ | Serve original PDF |
| GET | `/api/library` | ✅ | All user documents |
| GET | `/api/notifications` | ✅ | Recent audit notifications |
| POST | `/api/chat` | ✅ | RAG chat with document |
| POST | `/api/compare` | ✅ | Compare two documents |
| POST | `/api/compliance/check` | ✅ | Run compliance check |
| GET | `/api/export/{id}?format=pdf` | ✅ | Export audit as PDF |
| GET | `/api/export/{id}?format=docx` | ✅ | Export audit as DOCX |

---

## 12. Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'X'` | Run `pip install X` (replace X with the module name) |
| `python-multipart` error on file upload | `pip install python-multipart` |
| `langchain_huggingface` not found | `pip install langchain-huggingface sentence-transformers` |
| Gemini API 503 or 429 error | The app auto-retries with fallback models. If persistent, wait 1-2 minutes |
| CORS errors in browser | Ensure backend is on port 8000 and frontend on 5173 |
| MongoDB connection refused | Check your `MONGO_URI` in `.env`. For Atlas, ensure IP whitelist is set |
| Pinecone connection error | Verify `PINECONE_API_KEY` and `PINECONE_HOST` in `.env` |
| HuggingFace model download slow | Normal on first run (~80MB). Requires internet connection |
| `[Cache] REDIS_URL not set` message | Expected if you didn't set up Redis. App works fine without it |
| Frontend won't start | Run `npm install` again, then `npm run dev` |
| Virtual environment not activating | Windows: `.\venv\Scripts\activate`. Mac: `source venv/bin/activate` |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 + Vite | UI Framework |
| Styling | Tailwind CSS 3.4 | Utility-first CSS |
| Animations | Framer Motion | Page transitions & micro-animations |
| Icons | Lucide React | Icon library |
| Backend | FastAPI (Python) | REST API server |
| Auth | PyJWT + bcrypt | Token-based authentication |
| Database | MongoDB + Motor | Async document storage |
| Vector DB | Pinecone (Starter) | Semantic search over embeddings |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` | 384-dim sentence embeddings |
| AI / LLM | Google Gemini 2.0 Flash | Document analysis, chat, comparison, compliance |
| PDF Parser | PyMuPDF | Extract text from PDFs |
| Orchestration | LangChain | LLM prompt templates & integrations |
| Caching | Redis / Upstash | Chat response caching (optional) |
| Reports | ReportLab + python-docx | PDF/DOCX export |
| Deployment | Docker + Render.com | Containerization & cloud hosting |
