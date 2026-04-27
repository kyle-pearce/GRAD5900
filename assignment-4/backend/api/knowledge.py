from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..knowledge.retriever import query_knowledge
from ..knowledge.ingest import ingest_single, ingest_directory, get_collection
from ..core.config import settings

router = APIRouter(prefix="/api/knowledge")


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
async def query(req: QueryRequest):
    result = query_knowledge(req.question)
    return {
        "chunks": result["chunks"],
        "relevance_score": result["meta"]["relevance_score"],
        "corrected": result["meta"]["corrected"],
        "expanded_query": result["meta"].get("expanded_query"),
    }


class IngestRequest(BaseModel):
    path: str
    is_directory: bool = False


@router.post("/ingest")
async def ingest(req: IngestRequest):
    if req.is_directory:
        count = ingest_directory(req.path)
    else:
        count = ingest_single(req.path)
    if count == 0:
        raise HTTPException(status_code=400, detail="No chunks ingested — check the path and file type")
    return {"chunks_ingested": count, "path": req.path}


@router.get("/stats")
async def stats():
    collection = get_collection()
    return {
        "collection": collection.name,
        "document_count": collection.count(),
        "chroma_dir": str(settings.chroma_dir),
    }
