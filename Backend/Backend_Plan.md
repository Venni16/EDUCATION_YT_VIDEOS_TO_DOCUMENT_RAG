Build a production-ready backend using Node.js (Express) with Redis and BullMQ.

---

## 🧱 REQUIREMENTS

The backend acts as a gateway between frontend and AI service.

Responsibilities:

* Rate limiting
* Queueing
* Job tracking
* API routing

---

## 📬 API ENDPOINTS

1. POST /api/generate

* Input: { url }
* Extract videoId from YouTube URL
* Generate thumbnail:
  https://img.youtube.com/vi/{videoId}/0.jpg
* Add job to BullMQ queue
* Store metadata in Redis:
  job:{id}:meta
* Return:
  { jobId, videoId, thumbnail }

---

2. GET /api/status/:jobId

* Return job state:
  waiting / active / completed / failed

---

3. GET /api/result/:jobId

* Fetch from Redis:
  job:{id}:result
* Return:

  * title
  * thumbnail
  * document
  * pdf_url

---

4. GET /api/all-jobs

* Fetch all job metadata from Redis
* Return array of jobs

---

## 🚦 RATE LIMITING

* Use express-rate-limit + Redis
* Limit: 5 requests/minute per IP

---

## 📬 QUEUE SYSTEM (BullMQ)

* Queue name: "video-processing"
* Use Redis as backend
* Worker:

  * Calls FastAPI endpoint
  * Stores result in Redis

---

## ⚡ REDIS USAGE

Use Redis for:

1. Rate limiting
2. Queue backend
3. Job metadata:
   job:{id}:meta
4. Job results:
   job:{id}:result

---

## 🔄 WORKER LOGIC

Worker should:

1. Receive job
2. Call FastAPI:
   POST /generate-doc
3. Store response in Redis
4. Update job status

---

## ⚙️ CONFIG

* Use environment variables:

  * REDIS_HOST
  * FASTAPI_URL
* Enable CORS
* Add error handling

---

## 📁 OUTPUT

Provide full project:

backend/

* server.js
* queue.js
* worker.js
* redis.js
* routes/

Include:

* Full working code
* Redis connection
* BullMQ setup
* API endpoints

---

## 🎯 GOAL

A scalable backend that:

* Handles async jobs
* Prevents overload
* Stores and serves results efficiently
