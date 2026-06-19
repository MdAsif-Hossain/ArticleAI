<div align="center">
  <h1>🚀 AI Article Analyzer & Workflow Automation</h1>
  <p>An end-to-end full-stack agentic workflow combining FastAPI, n8n, and Groq Llama 3 to scrape, summarize, and distribute web content automatically.</p>
</div>

---

## 📺 Project Demo
*(Upload your demo video to a GitHub Issue, then copy the link and paste it here!)*
> [Watch the Demo Video Here](#)

## 🗺️ The n8n Workflow
*(Take a screenshot of your beautiful n8n canvas, upload it to a GitHub issue, and paste the image link here!)*
> ![Workflow Screenshot](#)

---

## 💡 About the Project
This project is a fully automated AI orchestration tool designed to ingest web articles, process them using Large Language Models, and distribute the extracted intelligence. It demonstrates how to seamlessly bridge a custom Python/FastAPI backend with a low-code workflow engine (n8n) using asynchronous webhooks.

When a user submits an article URL through the glassmorphism UI, the system:
1. **Scrapes** the raw text from the target website.
2. **Processes** the text sequentially through **Groq (Llama-3.3-70b)** to generate both a concise summary and actionable insights.
3. **Logs** the processed data into a Google Spreadsheet for record-keeping.
4. **Emails** a formatted HTML report to the user.
5. **Calls back** to the FastAPI backend to update the frontend UI in real-time.

## 🛠️ Tech Stack & Skills Demonstrated
This project serves as a showcase for modern backend orchestration and AI integration:

- **Backend Architecture**: `Python`, `FastAPI`, `Pydantic`, `Uvicorn`
- **Workflow Automation**: `n8n` (Webhook listeners, HTTP requests, sequential processing, error handling)
- **AI Integration**: `Groq API`, `Llama-3.3-70b`, Prompt Engineering
- **External APIs**: `Google Sheets OAuth2 API`, `Gmail SMTP`, Web Scraping
- **Frontend**: Vanilla `HTML/CSS/JS`, asynchronous polling, Glassmorphism UI
- **DevOps**: `Localtunnel` for exposing local webhooks to cloud services

---

## 🏗️ System Architecture

1. **Client (Browser)**: Sends a POST request with an email and article URL. Polls the backend for completion status.
2. **FastAPI (Backend)**: Generates a unique `session_id` and forwards the payload (including a dynamically generated callback URL) to the n8n Cloud Webhook.
3. **n8n (Orchestrator)**:
   - Receives payload and scrapes the target URL.
   - Summarizes text using Groq's Llama 3 model.
   - Extracts insights sequentially using Groq.
   - Merges metadata, summary, and insights.
   - Appends a new row to Google Sheets.
   - Dispatches an HTML email via SMTP.
   - Hits the FastAPI Callback URL to signal completion.
4. **FastAPI (Callback)**: Updates the session state to `completed`.
5. **Client (Browser)**: Receives the completed state and renders the summary and insights dynamically.

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.9+
- Node.js (for Localtunnel)
- n8n Cloud account
- Groq API Key

### 1. Start the Tunnel
To allow n8n Cloud to talk back to your local machine, run:
```bash
npx localtunnel --port 8000 --subdomain your-unique-name
```

### 2. Configure the Backend
Navigate to the `backend` folder and copy `.env.example` to `.env`:
```env
N8N_WEBHOOK_URL=https://your-n8n-url.app.n8n.cloud/webhook/process-article
BACKEND_CALLBACK_URL=https://your-unique-name.loca.lt/api/callback
```

### 3. Start the FastAPI Server
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 4. Import the n8n Workflow
1. Go to your n8n workspace.
2. Import the `n8n/workflow.json` file.
3. Add your Groq API key directly to the AI nodes (`Bearer gsk_...`).
4. Authenticate your Google Sheets and SMTP credentials.
5. Set the workflow to **Active**.

### 5. Test it out
Open `http://localhost:8000` in your browser, enter an article link, and watch the automation run!
