from fastapi import APIRouter, HTTPException, BackgroundTasks
import httpx
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict

from models import ProcessRequest, ProcessResponse, StatusResponse, N8nCallback
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory session store
sessions: Dict[str, dict] = {}


async def forward_to_n8n(session_id: str, email: str, article_url: str):
    """Sends the payload to the n8n webhook in the background."""
    payload = {
        "session_id": session_id,
        "email": email,
        "article_url": article_url,
        "callback_url": settings.backend_callback_url,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.n8n_webhook_url,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            logger.info(f"✅ Forwarded session {session_id} to n8n — status {response.status_code}")
    except httpx.ConnectError:
        logger.error(f"❌ Cannot reach n8n at {settings.n8n_webhook_url}")
        if session_id in sessions:
            sessions[session_id]["status"] = "error"
            sessions[session_id]["error"] = (
                "Cannot reach n8n. Make sure your n8n instance is running "
                "and the webhook URL in .env is correct."
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ n8n returned HTTP {e.response.status_code}")
        if session_id in sessions:
            sessions[session_id]["status"] = "error"
            sessions[session_id]["error"] = f"n8n returned error: {e.response.status_code}"
    except Exception as e:
        logger.error(f"❌ Unexpected error forwarding to n8n: {e}")
        if session_id in sessions:
            sessions[session_id]["status"] = "error"
            sessions[session_id]["error"] = "Failed to contact n8n processing server."


# ────────────────────────────────────────────────
# POST /api/process
# ────────────────────────────────────────────────
@router.post("/process", response_model=ProcessResponse)
async def process_article(request: ProcessRequest, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "status": "processing",
        "summary": None,
        "insights": None,
        "article_url": str(request.article_url),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "error": None,
    }

    background_tasks.add_task(
        forward_to_n8n,
        session_id=session_id,
        email=str(request.email),
        article_url=str(request.article_url),
    )

    logger.info(f"📝 Created session {session_id}")

    return ProcessResponse(
        session_id=session_id,
        status="processing",
        message="Request received — n8n workflow started.",
    )


# ────────────────────────────────────────────────
# GET /api/status/{session_id}
# ────────────────────────────────────────────────
@router.get("/status/{session_id}", response_model=StatusResponse)
async def get_status(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    s = sessions[session_id]

    return StatusResponse(
        session_id=session_id,
        status=s["status"],
        summary=s.get("summary"),
        insights=s.get("insights"),
        article_url=s.get("article_url"),
        created_at=s.get("created_at"),
        error=s.get("error"),
    )


# ────────────────────────────────────────────────
# POST /api/callback  (called by n8n)
# ────────────────────────────────────────────────
@router.post("/callback")
async def n8n_callback(callback: N8nCallback):
    """Endpoint for n8n to POST results back when finished."""
    sid = callback.session_id

    if sid not in sessions:
        sessions[sid] = {}

    sessions[sid].update(
        {
            "status": callback.status,
            "summary": callback.summary,
            "insights": _parse_insights(callback.insights),
            "error": callback.error,
        }
    )

    logger.info(f"📬 Callback received for session {sid} — status: {callback.status}")
    return {"message": "Callback received", "session_id": sid}


def _parse_insights(insights_data) -> list[str]:
    """Normalise insights into a clean list of strings."""
    if not insights_data:
        return []
    if isinstance(insights_data, list):
        return [str(i).strip() for i in insights_data if str(i).strip()]
    if isinstance(insights_data, str):
        lines = [
            line.lstrip("-•*0123456789.) ").strip()
            for line in insights_data.split("\n")
            if line.strip()
        ]
        return lines if lines else [insights_data]
    return [str(insights_data)]
