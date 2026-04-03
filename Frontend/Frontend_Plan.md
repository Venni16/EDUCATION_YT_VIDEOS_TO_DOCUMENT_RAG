Build a modern frontend using React (Vite) and Tailwind CSS for an AI-powered YouTube document generation system.

---

## 🧱 REQUIREMENTS

Create a clean, responsive UI with 3 main pages:

1. Generate Page
2. Results Page
3. Viewer Page

Use React Router for navigation.

---

## 📄 PAGE DETAILS

1. Generate Page:

* Input field for YouTube URL
* Submit button ("Generate Document")
* Show loading state
* After submit:

  * Display Job ID
  * Show status: "Processing..."

---

2. Results Page:

* Fetch from: GET /api/all-jobs
* Display a grid of cards
* Each card must include:

  * YouTube thumbnail
  * Title
  * Status (processing / completed)
  * Button:

    * "View Document" (only if completed)

---

3. Viewer Page:

* Fetch from: GET /api/result/:jobId
* Display:

  * Thumbnail
  * Title
  * Render document (Markdown formatted)
  * Button: Download PDF

---

## 🎨 UI DESIGN (Tailwind)

* Use modern dashboard style
* Cards:

  * rounded-2xl
  * shadow-md
  * hover:scale-105
* Layout:

  * grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3
* Typography:

  * clean spacing
  * readable text

---

## ⚙️ STATE MANAGEMENT

* Use React hooks (useState, useEffect)
* Handle:

  * loading
  * error
  * success states

---

## 🔌 API INTEGRATION

Create a service file:

* POST /api/generate
* GET /api/status/:jobId
* GET /api/result/:jobId
* GET /api/all-jobs

---

## 🔄 POLLING

* After generating a job:

  * Poll status every 3–5 seconds
  * Update UI when completed

---

## ✨ EXTRA FEATURES

* Loader spinner
* Toast notifications
* Error handling UI
* Empty state UI

---

## 📁 OUTPUT

Provide full project structure:

src/

* pages/
* components/
* services/
* App.jsx
* main.jsx

Include:

* Complete working code
* Tailwind config
* Routing setup
* API integration

---

## 🎯 GOAL

A clean, responsive frontend that:

* Accepts YouTube links
* Tracks processing
* Displays results with thumbnail + document
