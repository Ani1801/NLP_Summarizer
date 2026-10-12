# AI Legal Document Intelligence — Group Task Allocation & Technical Blueprint

This document outlines the complete architectural division of the **AI Legal Document Intelligence Application** into **4 distinct, self-contained modules** for a team of 4 software engineers.

---

## 🏗️ Architecture & Tech Stack Summary
* **Frontend**: React (Vite), TailwindCSS, Lucide Icons, Context API (`AuthContext`), Fetch API (`api.js`).
* **Backend**: FastAPI (Python 3.10+), Pydantic v2, `google-auth`, JWT (`python-jose`/`pyjwt`), `passlib[bcrypt]`.
* **AI & RAG Pipeline**: LangChain / Sentence-Transformers (`all-MiniLM-L6-v2`), Pinecone Vector Database, PyPDF / pdfplumber.
* **Database & Cache**: MongoDB (Async Motor driver), Redis (Caching service).

---

## 📋 Team Work Distribution Overview

| Member | Module Role | Core Domain & Focus Area | Key Target Files |
|---|---|---|---|
| **Member 1** | **User Access, Dashboard & Document Repository** | Auth (Email + Google OAuth), User Roles, Settings, Analytics Dashboard, and Document Library | `Auth.jsx`, `Dashboard.jsx`, `Library.jsx`, `Settings.jsx`, `auth.py`, `dashboard.py`, `library.py`, `auth_service.py`, `google_auth_service.py` |
| **Member 2** | **PDF Processing, Vector Store & Legal Risk Audit** | PDF Ingestion, Text Chunking, Vector Embeddings (Pinecone), Risk Clause Detection & Key Entity Extraction | `AuditNew.jsx`, `processor.py`, `vector_store.py`, `audit_service.py`, `audits.py`, `schemas/user.py` |
| **Member 3** | **RAG AI Chat, Source Citations & Global Assistant** | Semantic Vector Retrieval, Grounded Q&A LLM Engine, Pinpoint Citation System, Interactive Chat Panel & Floating Widget | `ChatPanel.jsx`, `FloatingChatWidget.jsx`, `SourceCitation.jsx`, `chat.py`, `chat_service.py`, `query_service.py` |
| **Member 4** | **Contract Comparison, Regulatory Compliance & Exporter** | Side-by-Side Diff Analysis, Compliance Rule Engine (GDPR, HIPAA, SOC 2), PDF/DOCX Exporter & Cache Optimization | `Compare.jsx`, `Compliance.jsx`, `compare.py`, `compliance.py`, `export.py`, `compare_service.py`, `compliance_service.py`, `export_service.py` |

---

---

# 👤 Member 1: User Access, Settings, Dashboard & Document Library

### 🎯 Primary Scope
Member 1 is responsible for the user lifecycle, identity management, settings customization, user activity tracking, and the central document repository system.

### 🛠️ Detailed Feature Breakdown & Technical Approach

#### 1. Authentication & Identity Engine (Email/Password + Google OAuth)
* **Features**:
  * Dual login/signup flow: Traditional Email/Password + Google Identity Services ("Continue with Google").
  * Automatic account linking: If a user signs in with Google using an email that already exists via local signup, automatically link `google_sub` to the user profile without losing existing audit history.
  * JWT Session Token lifecycle management with 24-hour expiration.
* **Detailed Approach**:
  * **Frontend**: Handle state in `AuthContext.jsx` and `Auth.jsx`. Render `GoogleSignInButton` dynamically using `https://accounts.google.com/gsi/client`. Handle auth errors via `api.js`.
  * **Backend**: Implement `POST /api/auth/signup`, `POST /api/auth/login`, and `POST /api/auth/google` in `app/api/auth.py`. Cryptographically verify Google ID token in `google_auth_service.py` using `google-auth`.
  * **Database**: MongoDB `users` collection with unique index on `email` and sparse unique index on `google_sub`.

#### 2. Profile & Settings Management (`Settings.jsx`)
* **Features**:
  * View and update personal information (Full Name, Role: `Lawyer` / `Researcher` / `Student` / `Professional`).
  * Security tab: Password change workflow with current password verification.
  * Preferences: AI Analysis rigor settings (Strict, Standard, Granular), notification toggles.
* **Detailed Approach**:
  * **Frontend**: Build structured tabbed UI in `Settings.jsx` with real-time feedback toasts and form validation.
  * **Backend**: Endpoints `GET /api/user/profile` and `PUT /api/user/profile` for updating user metadata.

#### 3. Analytics Dashboard & Recent Activity (`Dashboard.jsx`, `dashboard.py`)
* **Features**:
  * High-level statistical cards: Total Audits Run, High-Risk Clauses Detected, Active Contracts, Average Risk Score.
  * Quick-start action cards: "Upload New Audit", "Compare Documents", "Check Compliance".
  * Recent Audits Table: View recent documents with risk indicator badges, contract types, and date processed.
* **Detailed Approach**:
  * **Frontend**: `Dashboard.jsx` using `StatCards.jsx` and `RecentAudits.jsx`.
  * **Backend**: `GET /api/dashboard/stats` aggregating metrics from `audits` and `documents` MongoDB collections using Motor aggregation pipelines.

#### 4. Document Library Repository (`Library.jsx`, `library.py`, `document_service.py`)
* **Features**:
  * Document storage index with metadata (File Name, File Size, Upload Date, Risk Rating, Processing Status).
  * Search, filter by risk level (High/Med/Low), and sort by date.
  * Document actions: View audit details, re-download original PDF, soft delete document.
* **Detailed Approach**:
  * **Frontend**: Datatable grid in `Library.jsx` with search filter bar and action dropdowns.
  * **Backend**: `GET /api/library/documents`, `DELETE /api/library/documents/{doc_id}` in `library.py` and `document_service.py`.

### 📂 Target Files (Member 1)
* `frontend/src/pages/Auth.jsx`
* `frontend/src/pages/Settings.jsx`
* `frontend/src/pages/Dashboard.jsx`
* `frontend/src/pages/Library.jsx`
* `frontend/src/context/AuthContext.jsx`
* `frontend/src/services/api.js`
* `backend/app/api/auth.py`
* `backend/app/api/dashboard.py`
* `backend/app/api/library.py`
* `backend/app/services/auth_service.py`
* `backend/app/services/google_auth_service.py`
* `backend/app/services/document_service.py`
* `backend/app/schemas/user.py`

---

---

# 👤 Member 2: PDF Processing Pipeline, Vector Store & Legal Risk Audit

### 🎯 Primary Scope
Member 2 is responsible for document ingestion, text parsing, vector embedding generation, Pinecone indexing, and the core single-document AI risk audit engine.

### 🛠️ Detailed Feature Breakdown & Technical Approach

#### 1. PDF Ingestion, Text Extraction & Chunking Engine (`processor.py`, `storage_service.py`)
* **Features**:
  * Secure PDF upload handling with file type validation (PDF format check, file size limits).
  * Clean text extraction preserving original page numbers, headings, and paragraph boundaries.
  * Legal-aware text chunking: Splitting document by clause boundaries / logical sections (500–1000 characters with 100 character overlap) while tagging each chunk with `page_number` and `section_title`.
* **Detailed Approach**:
  * Use `pdfplumber` / `PyPDF2` in `app/services/ai/processor.py`.
  * Store original PDF files in `uploads/` directory via `storage_service.py`.

#### 2. Vector Store Indexing & Embedding Pipeline (`vector_store.py`)
* **Features**:
  * Convert extracted text chunks into 384-dimensional dense vector embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
  * Upsert vector embeddings into **Pinecone Vector Database** under isolated user namespaces (`user_{user_id}`).
  * Store chunk metadata (`doc_id`, `page_number`, `clause_type`, `raw_text`) alongside vectors.
* **Detailed Approach**:
  * Maintain vector upsert and query functions in `app/services/ai/vector_store.py`.
  * Handle graceful fallback to local memory vector index if Pinecone API key is unavailable.

#### 3. Clause Classification & Risk Analysis Engine (`audit_service.py`, `audits.py`)
* **Features**:
  * Automated identification and classification of 7+ core legal clause categories:
    1. *Termination & Renewal*
    2. *Payment & Financial Terms*
    3. *Limitation of Liability*
    4. *Indemnification & Hold Harmless*
    5. *Confidentiality & Non-Disclosure*
    6. *Governing Law & Dispute Resolution*
    7. *Intellectual Property Rights*
  * Severity Tagging: Flag every clause as **Low Risk**, **Medium Risk**, **High Risk**, or **Critical Risk**.
  * Plain-English explanation generation: Explaining complex legalese in clear language with recommendations.
* **Detailed Approach**:
  * **Backend**: Multi-stage LLM prompt pipeline in `app/services/ai/audit_service.py`. Compute overall Document Health / Risk Score (0-100%).
  * **API Endpoint**: `POST /api/audits/upload` and `GET /api/audits/{audit_id}` in `app/api/audits.py`.

#### 4. Key Entity Extraction & Multi-Level Summarization (`AuditNew.jsx`)
* **Features**:
  * Executive High-Level Summary, Key Risk Highlights, and Section-by-Section Accordion Breakdown.
  * Structured Key Entity Grid:
    * *Parties & Organizations* (Company name, contracting entity, address).
    * *Key Dates & Timeline* (Effective date, expiration date, notice period).
    * *Financial Values* (Contract value, payment terms, penalty fees, liability caps).
    * *Jurisdiction* (Governing law state/country, arbitration venue).
* **Detailed Approach**:
  * **Frontend**: Tabbed interface in `AuditNew.jsx` (*Summary*, *Clauses*, *Entities*, *Q&A Chat*).
  * **Database**: Save complete audit results in MongoDB `audits` collection for persistent fast loading.

### 📂 Target Files (Member 2)
* `frontend/src/pages/AuditNew.jsx`
* `backend/app/api/audits.py`
* `backend/app/services/ai/processor.py`
* `backend/app/services/ai/vector_store.py`
* `backend/app/services/ai/audit_service.py`
* `backend/app/services/storage_service.py`

---

---

# 👤 Member 3: RAG AI Chat, Source Citations & Global Assistant

### 🎯 Primary Scope
Member 3 is responsible for the Retrieval-Augmented Generation (RAG) Q&A engine, strict context grounding, pinpoint source citation tracking, and interactive chat interfaces.

### 🛠️ Detailed Feature Breakdown & Technical Approach

#### 1. RAG Vector Search & Retrieval Engine (`query_service.py`)
* **Features**:
  * Natural language question processing for legal contracts.
  * Embed user question with `all-MiniLM-L6-v2` and perform cosine similarity search against Pinecone vector store.
  * Retrieve top-K (K=4 to 6) most relevant contract chunks restricted to the specific document ID and user namespace.
* **Detailed Approach**:
  * Implement `query_document_chunks()` in `app/services/ai/query_service.py`.

#### 2. Grounded AI Q&A Engine (`chat_service.py`, `chat.py`)
* **Features**:
  * Zero-hallucination constraint: Ensure LLM answers questions strictly using provided contract snippets. If answer is not in contract, return explicit notification.
  * Provide structured response format: Answer text + array of source citations (`page_number`, `clause_type`, `verbatim_quote`).
* **Detailed Approach**:
  * **Backend**: System prompt design in `app/services/ai/chat_service.py`.
  * **API Endpoint**: `POST /api/chat/query` in `app/api/chat.py`.

#### 3. Pinpoint Citation System (`SourceCitation.jsx`, UI Badges)
* **Features**:
  * Clickable citation badges in AI responses (e.g. `[Page 3 • Section 5.2]`).
  * Interactive Hover Preview / Drawer: Hovering or clicking a citation badge opens a drawer showing the exact verbatim clause text highlighted from the source PDF.
* **Detailed Approach**:
  * **Frontend**: Build reusable component `SourceCitation.jsx`.
  * Bind citation badges seamlessly into summary text, audit clause cards, and chat messages.

#### 4. Interactive Chat Interfaces (`ChatPanel.jsx`, `FloatingChatWidget.jsx`)
* **Features**:
  * Full-width Q&A panel embedded inside document audit page (`ChatPanel.jsx`).
  * Quick-prompt chips (*"What is the notice period for termination?"*, *"Is there a liability cap?"*, *"What are the payment terms?"*).
  * Persistent Floating Chat Drawer (`FloatingChatWidget.jsx`): Allows querying contracts from anywhere in the application.
  * Conversation history retention per session.
* **Detailed Approach**:
  * **Frontend**: `ChatPanel.jsx` and `FloatingChatWidget.jsx` integrated into main layout.

### 📂 Target Files (Member 3)
* `frontend/src/components/ChatPanel.jsx`
* `frontend/src/components/FloatingChatWidget.jsx`
* `frontend/src/components/SourceCitation.jsx`
* `backend/app/api/chat.py`
* `backend/app/services/ai/query_service.py`
* `backend/app/services/ai/chat_service.py`

---

---

# 👤 Member 4: Contract Comparison, Regulatory Compliance & Exporter

### 🎯 Primary Scope
Member 4 is responsible for multi-document version comparison, automated regulatory compliance auditing (GDPR, HIPAA, SOC 2), PDF/DOCX report exports, and system caching optimizations.

### 🛠️ Detailed Feature Breakdown & Technical Approach

#### 1. Interactive Contract Comparison Engine (`Compare.jsx`, `compare.py`, `compare_service.py`)
* **Features**:
  * Side-by-side split screen view comparing Document A (Baseline/Standard Contract) vs Document B (Vendor/Modified Contract).
  * Automated Clause Alignment & Diff Analysis:
    * **Added Clauses** (Highlighted in Green)
    * **Removed Clauses** (Highlighted in Red)
    * **Modified Clauses** (Highlighted in Amber with side-by-side diff)
  * Overall **Risk Shift Score** (e.g., *"+15% Higher Risk in Vendor Draft"*).
* **Detailed Approach**:
  * **Backend**: Pairwise clause matching algorithm in `compare_service.py`. Compare key legal terms across both documents.
  * **API Endpoint**: `POST /api/compare` in `app/api/compare.py`.
  * **Frontend**: Dual file selector and split-view visual diff UI in `Compare.jsx`.

#### 2. Regulatory Compliance Checker (`Compliance.jsx`, `compliance.py`, `compliance_service.py`)
* **Features**:
  * Select target regulatory standard:
    * **GDPR** (Data Protection, Subprocessor clauses, Breach notification)
    * **HIPAA** (BAA requirements, PHI handling)
    * **SOC 2** (Security incident response, Data encryption)
    * **Indian Contract Act / Standard Commercial Law** (Unenforceable terms, Penalty clauses)
  * Overall Compliance Score Gauge (0–100%).
  * Violation Flags & Recommended Remediation Wording.
* **Detailed Approach**:
  * **Backend**: Rule-based + LLM evaluation matrix in `compliance_service.py`.
  * **API Endpoint**: `POST /api/compliance/check` in `app/api/compliance.py`.
  * **Frontend**: Compliance dashboard view in `Compliance.jsx`.

#### 3. Formal Report Export Engine (`export.py`, `export_service.py`)
* **Features**:
  * Generate downloadable audit reports in **PDF** and **DOCX** formats.
  * Executive summary section, risk matrix table, detailed clause breakdown, and compliance certificate.
  * Custom branding with company logo, timestamp, and auditor sign-off.
* **Detailed Approach**:
  * **Backend**: Generate PDF via `reportlab` and DOCX via `python-docx` in `export_service.py`.
  * **API Endpoints**: `GET /api/export/pdf/{audit_id}` and `GET /api/export/docx/{audit_id}` in `app/api/export.py`. Handle streaming binary response in `api.js` (`getStream`).

#### 4. Cache & Performance Optimization (`cache_service.py`)
* **Features**:
  * Redis / In-memory LRU caching layer for heavy LLM responses and vector query lookups.
  * Prevents duplicate embedding calls for identical document chunks.
* **Detailed Approach**:
  * Implement caching decorator / service in `app/services/cache_service.py`.

### 📂 Target Files (Member 4)
* `frontend/src/pages/Compare.jsx`
* `frontend/src/pages/Compliance.jsx`
* `backend/app/api/compare.py`
* `backend/app/api/compliance.py`
* `backend/app/api/export.py`
* `backend/app/services/ai/compare_service.py`
* `backend/app/services/ai/compliance_service.py`
* `backend/app/services/export_service.py`
* `backend/app/services/cache_service.py`

---

---

## 🧪 Integration & End-to-End Verification Roadmap

Once all 4 members complete their individual modules:
1. **Auth & Session Handoff**: Member 1 provides authenticated JWT headers to all frontend API calls made by Members 2, 3, and 4.
2. **Document Pipeline Handoff**: Member 2 processes uploaded PDFs, populates MongoDB `audits` and Pinecone vector store, providing `doc_id` and `audit_id` to Members 3 and 4.
3. **Chat & Citation Handoff**: Member 3 uses vector indices populated by Member 2 to serve Q&A with pinpoint citations.
4. **Comparison & Export Handoff**: Member 4 uses document data from Member 2 to compute comparison diffs, run compliance checks, and export final PDF/DOCX reports.
