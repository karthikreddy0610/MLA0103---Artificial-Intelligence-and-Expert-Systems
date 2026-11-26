# CityBrain - Smart Urban Grievance & Complaint Tracking System

A full-stack, connected urban management platform that connects citizens to municipal departments with automated AI priority triaging and real-time status tracking.

---

## 📁 Connected Folder Architecture

```text
City Brainn/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Backend package initialization
│   │   ├── main.py              # FastAPI server, REST API endpoints, CORS, & static mounting
│   │   ├── models.py            # Pydantic data contracts (ComplaintInput, PromptAnalysisInput, etc.)
│   │   ├── nlp_analyzer.py      # Transformer & NLP Prompt Analyzer & Semantic Understanding Algorithm
│   │   ├── priority.py          # Unified AI priority & municipal department classification interface
│   │   └── database.py          # Persistent JSON database with Cosine Similarity Anti-Duplicate verification
│   ├── data/
│   │   ├── complaints.json      # Persistent storage records
│   │   └── notices.json         # Municipal announcements & alerts
│   ├── requirements.txt         # FastAPI, Uvicorn, Pydantic, Transformers dependencies
│   └── run.py                   # Dedicated backend launcher with automatic browser opening
├── frontend/
│   ├── index.html               # Modern Light UI Web Portal (Citizen Portal, Tracker, Admin Command)
│   ├── css/
│   │   └── style.css            # Light modern design system, glassmorphism, responsive styles
│   └── js/
│       ├── api.js               # Unified API client (FastAPI on port 8000 + LocalStorage fallback)
│       └── app.js               # Reactive UI controller, real-time NLP prompt triage, tracker, admin
├── main.py                      # Root FastAPI application entry point
├── run.py                       # One-command project runner (launches server + opens web UI)
├── start.bat                    # Windows 1-click launcher
└── README.md                    # Project documentation
```

---

## 🧠 DistilBERT Complaint Understanding Engine

The **Complaint Understanding Engine** focuses strictly on language representation and understanding before any downstream decisions (Priority, Department Routing, or Duplicate Detection) are made.

### The Exact 4-Step Pipeline:

```text
USER COMPLAINT (Raw Text)
          ↓
DISTILBERT TOKENIZER
          ↓
[CLS] Token IDs + Attention Mask [SEP]
          ↓
DISTILBERT (6 Transformer Layers)
          ↓
MULTI-HEAD SELF-ATTENTION & CONTEXT PROCESSING
          ↓
CONTEXTUAL EMBEDDINGS (768-dimensional vector)
          ↓
COMPLAINT MEANING REPRESENTATION
```

1. **Step 1: Text Input → DistilBERT Tokenizer**:
   Converts the raw text into token IDs and attention mask wrapped with `[CLS]` and `[SEP]`.
2. **Step 2: Token IDs → DistilBERT Model**:
   Processes the relationship and contextual connection between words (e.g. connecting *"people are getting injured"* to *"huge pothole"*).
3. **Step 3: 6 Transformer Layers**:
   Applies Self-Attention and Feed-Forward Networks across all 6 Transformer layers.
4. **Step 4: Contextual Embeddings (768 Dimensions)**:
   Outputs the machine-understandable contextual embedding vector representing the core meaning of the complaint.

> **Faculty Answer:**
> *"For complaint understanding, we use DistilBERT. First, the raw complaint text is processed by the DistilBERT tokenizer, which converts the text into token IDs and an attention mask. These are passed through DistilBERT's six Transformer layers, where self-attention helps understand the relationship and context between words. The final output is a contextual embedding representing the meaning of the complaint."*

---

## 🏛️ End-to-End System Architecture & Lifecycle Workflow

```text
┌─────────────────────────────────────────────────────────────┐
│                        USER / CITIZEN                       │
│                                                             │
│  Submit Complaint                                           │
│  • Complaint Text                                          │
│  • Location                                                │
│  • Optional Image                                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND APPLICATION                    │
│                                                             │
│  • Complaint Submission                                    │
│  • User Profile                                            │
│  • Complaint Tracking                                      │
│  • Admin Dashboard                                         │
└────────────────────────────┬────────────────────────────────┘
                             │ API Request
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                         │
│                                                             │
│  • API Endpoints                                            │
│  • Input Validation                                         │
│  • Authentication                                           │
│  • Business Logic                                           │
│  • Database Communication                                   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI TRIAGE ENGINE 🧠                      │
│                                                             │
│  STEP 1 → Complaint Understanding                           │
│  STEP 2 → Root Civic Asset Identification                   │
│  STEP 3 → Department Recommendation                         │
│  STEP 4 → Impact & Severity Analysis                        │
│  STEP 5 → Priority Assessment                               │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI TRIAGE RESULT                          │
│                                                             │
│  • Root Issue                                               │
│  • Recommended Department                                   │
│  • Priority                                                 │
│  • Explanation / Analysis                                   │
│                                                             │
│  STATUS → PENDING REVIEW                                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN DASHBOARD 👨💼                      │
│                                                             │
│  Review Complaint                                           │
│  Review AI Recommendation                                   │
│                                                             │
│        [ APPROVE & ASSIGN ]      [ REJECT ]                 │
└───────────────────┬──────────────────────┬──────────────────┘
                    │                      │
                    ▼                      ▼
         ┌─────────────────┐      ┌─────────────────┐
         │ APPROVED        │      │ REJECTED        │
         └────────┬────────┘      └────────┬────────┘
                  │                        │
                  ▼                        ▼
      ASSIGN TO RECOMMENDED         REJECTION REASON
      DEPARTMENT                         REQUIRED
                  │                        │
                  ▼                        ▼
            STATUS: ASSIGNED          STATUS: REJECTED
                  │                        │
                  ▼                        │
         DEPARTMENT DASHBOARD             │
                  │                        │
                  ▼                        ▼
             IN PROGRESS              USER PROFILE
                  │                        │
                  ▼                        │
              RESOLVED ◄──────────────────┘
```

---

## ⚡ How Backend & Frontend Are Connected

1. **Direct API Integration**:
   - `frontend/js/api.js` connects to the FastAPI backend at `http://localhost:8000`.
   - All complaint submissions (`POST /complaints`), status queries (`GET /complaints/{uid}`), and department updates (`PUT /complaints/{uid}/status`) communicate seamlessly over REST endpoints.
   - Real-time connection badge on the header indicates:
     - `🟢 FastAPI Backend Connected` when the Python server is live.
     - `⚡ Web Mode (Local Sync)` when opened directly as a standalone web app.

2. **Unified Web Hosting**:
   - The FastAPI backend (`backend/app/main.py`) mounts the `frontend/` directory directly under `/`.
   - When you start the backend, browsing to `http://localhost:8000` automatically serves the complete frontend application.

---

## 🚀 How to Run & Open in Web

### Option 1: Quick 1-Click Launch (Windows)
Double-click:
```cmd
start.bat
```

### Option 2: Python Command (Terminal)
Run from the project root:
```bash
pip install -r backend/requirements.txt
python run.py
```
This automatically starts FastAPI on port 8000 and opens `http://localhost:8000` in your default browser.

### Option 3: Direct Web Browser
You can also directly open `frontend/index.html` in Google Chrome, Microsoft Edge, or any modern browser. It comes pre-loaded with realistic municipal data and full interactive tracking.

---

## 🎨 Frontend Features (Modern Light UI)

- **AI Priority Triage**: Evaluates incident description text in real time as you type (Critical, High, Medium) and routes directly to the correct department (Fire, Power, Water, Roads, Sanitation, etc.).
- **Incident Status Tracker**: Visual 4-stage progression stepper from initial submission to final resolution with reference UID.
- **Department Command Center**: Live KPI cards, multi-criteria filtering, and inline status modification with instant UI updates.
- **Geolocation Integration**: One-click GPS location detection via browser geolocation API.

