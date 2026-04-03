Build a full-stack, production-ready AI system with the following architecture and features.

---

## 🧠 SYSTEM OVERVIEW

Create an AI-powered platform that:

1. Accepts a YouTube video URL
2. Extracts transcript data
3. Processes it using an Agentic RAG pipeline
4. Generates a structured, professional document
5. Stores results
6. Displays video thumbnail + generated document in a separate tab
7. Supports async processing with queueing and rate limiting

---

## 🏗️ TECH STACK

Frontend:

* React.js (Vite)
* Tailwind CSS

Backend:

* Node.js (Express.js)
* Redis (rate limit, cache, job storage)
* BullMQ (queue system)

AI Service:

* FastAPI (Python)
* Local LLM (Mistral / Llama via HuggingFace or Ollama)
* FAISS or Chroma (vector database)

---

## ⚙️ ARCHITECTURE

React (UI)
↓
Express API (Gateway)
├── Rate Limiting (Redis)
├── Queue (BullMQ + Redis)
└── Job APIs
↓
Worker (BullMQ)
↓
FastAPI (Agentic AI Service)
├── YouTube Tool
├── Retrieval Tool (Vector DB)
├── Summary Tool
├── LLM Processing
└── Document Generator

---

## 🔥 CORE FEATURES

1. Paste YouTube URL → Generate document
2. Async job processing (queue)
3. Rate limiting (5 req/min per user)
4. Redis caching (transcripts + LLM outputs)
5. Results dashboard (thumbnails + status)
6. Document viewer page
7. PDF generation + download

---

## 📦 FRONTEND REQUIREMENTS (React + Tailwind)

Create 3 main pages:

1. Generate Page:

* Input field for YouTube URL
* Submit button
* Show job ID and status

2. Results Page:

* Grid layout of processed videos
* Each card contains:

  * Thumbnail
  * Title
  * Status (processing/completed)
  * Button: View Document

3. Viewer Page:

* Show:

  * Video thumbnail
  * Title
  * Generated document (Markdown formatted)
  * Button: Download PDF

Design:

* Use Tailwind CSS
* Clean modern UI
* Responsive grid
* Card hover effects
* Loader/spinner during processing

---

## 🔌 BACKEND REQUIREMENTS (Express.js)

Implement APIs:

POST /api/generate

* Input: YouTube URL
* Extract videoId + thumbnail
* Push job to BullMQ queue
* Store metadata in Redis
* Return jobId

GET /api/status/:jobId

* Return job status

GET /api/result/:jobId

* Return:

  * title
  * thumbnail
  * document
  * pdf_url

GET /api/all-jobs

* Return list of all jobs with metadata

---

## 🚦 RATE LIMITING

* Use Redis-based rate limiting
* Limit: 5 requests per minute per IP

---

## 📬 QUEUE SYSTEM (BullMQ)

* Queue name: "video-processing"
* Worker processes jobs asynchronously
* Concurrency: 2–3 jobs
* Retry: 3 attempts with exponential backoff

---

## 🧠 AI SERVICE (FastAPI)

Build an Agentic RAG system with tools:

1. YouTube Tool:

* Extract transcript using youtube-transcript-api
* Fallback: yt-dlp + Whisper

2. Processing:

* Clean transcript
* Chunk into segments

3. Embedding:

* Convert chunks to vectors
* Store in FAISS/Chroma

4. Tools:

* Retrieval Tool → fetch relevant chunks
* Summary Tool → compress content
* Document Tool → generate structured document

5. Agent Logic:

* Detect input type
* Call tools dynamically
* Multi-step reasoning (ReAct pattern)

---

## 🧾 DOCUMENT GENERATION

Generate structured output:

* Title
* Abstract
* Table of Contents
* Sections with headings
* Bullet points
* Examples
* Conclusion

---

## 📄 PDF GENERATION

* Use reportlab (Python)
* Convert document to PDF
* Save file path
* Return PDF URL

---

## ⚡ REDIS USAGE

Use Redis for:

1. Rate limiting
2. Queue backend (BullMQ)
3. Caching:

   * transcript:{videoId}
   * llm:{hash}
4. Job storage:

   * job:{id}:meta
   * job:{id}:result

---

## 📊 DATA FLOW

1. User submits URL
2. Express:

   * Rate limit check
   * Add job to queue
3. Worker:

   * Calls FastAPI
4. FastAPI:

   * Agent processes video
   * Generates document + PDF
5. Result stored in Redis
6. Frontend polls and displays results

---

## ⚡ PERFORMANCE REQUIREMENTS

* Async processing (non-blocking)
* Redis caching
* Chunk-level processing
* Worker concurrency control
* Retry + timeout handling

---

## 📁 OUTPUT STRUCTURE

Provide full project structure:

frontend/
backend/
ai-service/

Include:

* All source code
* API integration
* Queue setup
* Redis config
* FastAPI agent system

---

## 🎯 FINAL GOAL

Build a scalable, production-ready AI system that converts YouTube videos into structured learning documents with:

* Agentic reasoning
* RAG pipeline
* Async processing
* Modern UI
* High performance

---

Generate COMPLETE working code for all components.
