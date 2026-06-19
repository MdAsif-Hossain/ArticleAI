import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import settings
from routes import process

# --------------- Logging ---------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)

# --------------- App ---------------
app = FastAPI(
    title="AI Agent API",
    description="Backend for the AI Agent Project — connects Frontend to n8n.",
    version="1.0.0",
)

# CORS (allow frontend, ngrok, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------- Routes ---------------
app.include_router(process.router, prefix="/api", tags=["process"])


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "n8n_webhook": settings.n8n_webhook_url,
        "callback_url": settings.backend_callback_url,
    }


# --------------- Serve Frontend ---------------
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    # Serve static assets (css, js, images)
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(FRONTEND_DIR / "index.html")


# --------------- Entrypoint ---------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
