# n8n Setup Guide — For First-Time Users (Cloud Edition)

This guide shows you how to set up your project using the **n8n Cloud 14-day free trial**.

---

## Step 1: Start the Tunnel

Because n8n Cloud runs on the internet, it cannot natively talk to your computer (`localhost`). We use a tunnel to create a temporary public link to your computer.

1. Open PowerShell in your project folder (`e:\AI Agent Project with n8n`).
2. Run this command:
   ```bash
   npx localtunnel --port 8000
   ```
3. It will give you a URL like: `https://funny-words-go.loca.lt`
4. **⚠️ KEEP THIS TERMINAL OPEN!** Do not close it while you are working.

---

## Step 2: Import the Workflow into n8n Cloud

1. Go to your n8n Cloud dashboard (e.g., `https://your-name.app.n8n.cloud`).
2. Delete any existing nodes on the canvas.
3. Click the **three dots menu (⋯)** in the top right.
4. Select **"Import from file..."**.
5. Select `n8n/workflow.json` from your project folder.

---

## Step 3: Set Up Credentials

The workflow has 3 nodes that need credentials (they have ⚠️ warning triangles).

### 1. AI Summarize & AI Insights (Groq)
We are using Groq because it is 100% free and lightning fast.
1. Get a free API key at [console.groq.com](https://console.groq.com) (starts with `gsk_...`).
2. Double click the **AI Summarize** node.
3. Replace `{{ $env.GROQ_API_KEY }}` with your actual API key.
4. Repeat this for the **AI Insights** node.

### 2. Google Sheets
1. Create a Blank Spreadsheet at [sheets.google.com](https://sheets.google.com) named `AI Article Analysis`.
2. Add these headers to Row 1: `SessionID`, `Email`, `URL`, `Summary`, `Insights`.
3. Copy the **Sheet ID** from the URL bar (the long string of letters/numbers between `/d/` and `/edit`).
4. In n8n, double-click the **Google Sheets** node.
5. Under "Credential", click **Create New Credential** → **Google Sheets OAuth2 API**.
6. Click the big **Sign in with Google** button. (This is 1-click easy on the Cloud!).
7. Once connected, paste your **Sheet ID** into the "Document ID" field.

### 3. Send Email (Gmail)
1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) and create an App Password named `n8n`. Copy the 16-character password.
2. In n8n, double-click the **Send Email** node.
3. Change the "From Email" to your Gmail address.
4. Under "Credential", click **Create New Credential** → **SMTP**.
5. Fill in:
   - Host: `smtp.gmail.com`
   - Port: `465`
   - SSL/TLS: `ON`
   - User: `your@gmail.com`
   - Password: `your16characterapppassword` (no spaces)

---

## Step 4: Update Your `.env` File

1. In n8n, double-click the **Webhook** node.
2. Click **Test Webhook URL** and copy the link.
3. Open `backend/.env` (or create it from `.env.example`).
4. Update the values:

```env
# Paste the Test Webhook URL from n8n
N8N_WEBHOOK_URL=https://your-workspace.app.n8n.cloud/webhook-test/process-article

# Paste your Localtunnel URL, and add /api/callback
BACKEND_CALLBACK_URL=https://funny-words-go.loca.lt/api/callback
```

---

## Step 5: Start the App!

1. Open a **second terminal** (leave localtunnel running in the first one!).
2. Start the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
3. Open your browser to `http://localhost:8000`.
4. Submit an article!
