from fastapi import FastAPI
from app.api.routes import router as api_router
import app.config  # noqa: F401  (loads env vars)

app = FastAPI(
    title="Q&A Support Bot (RAG)",
    version="0.1.0",
    description="Guided project: website -> crawl -> chunk -> embed -> vector store -> retrieve -> answer.",
)

app.include_router(api_router, prefix="/api", tags=["rag"])

# For local dev convenience: `python main.py`
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
