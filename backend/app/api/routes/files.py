from app.core.database import get_db, SessionLocal
from app.core.connection_manager import manager

from app.models.chunk import Chunk
from app.models.device import Device
from app.models.file import File as FileModel   # Avoid name conflict with fastapi 'File'
from app.models.chunk import Chunk             

from app.core.chunk_waiter import set_chunk_arrived
from app.core.database import get_db

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi import Request

from sqlalchemy.orm import Session
from pathlib import Path

from app.services.file_chunk_download import fetch_all_chunks_for_file, assemble_file_from_chunks
from app.core.constants import TEMP_CHUNK_DIR

router = APIRouter()

@router.get("/files/{file_id}/download")
async def download_file(file_id: int, db: Session = Depends(get_db)):
    try:
        # 1. Ensure all chunks are fetched locally
        chunks = await fetch_all_chunks_for_file(db, file_id, manager)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    final_path = TEMP_CHUNK_DIR / f"file_{file_id}.bin"

    try:
        # 2. Assemble chunks in order
        assemble_file_from_chunks(chunks, final_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 3. Serve assembled file
    return FileResponse(
        final_path,
        media_type="application/octet-stream",
        filename=f"file_{file_id}.bin"
    )
