from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.core.database import get_db
from app.models.chunk import Chunk

router = APIRouter()
TEMP_DIR = Path("./temp_chunks")

@router.get("/chunks/{chunk_id}/download")
def download_chunk(chunk_id: int, db: Session = Depends(get_db)):
    c = db.query(Chunk).filter(Chunk.chunk_id == chunk_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Chunk not found in DB")

    path = TEMP_DIR / f"chunk_{chunk_id}.bin"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Chunk file missing: {path}")

    return FileResponse(
        path=str(path),
        filename=f"chunk_{chunk_id}.bin",
        media_type="application/octet-stream"
    )
