from app.core.database import SessionLocal
from app.services.registration import register_device
from app.models.chunk import Chunk
from app.models.device import Device
from fastapi import APIRouter, Depends, HTTPException
from app.models.file import File as FileModel   # Avoid name conflict with fastapi 'File'
from app.models.chunk import Chunk             
from pydantic import BaseModel
from typing import List


router = APIRouter()

@router.post("/devices/register")
def register_device_endpoint(payload: dict):
    db = SessionLocal()
    try:
        result = register_device(
            db=db,
            user_id= payload["user_id"],
            device_name = payload["device_name"],
            storage_capacity= payload["storage_capacity"],
            available_storage=payload["available_storage"],
            fingerprint = payload["fingerprint"],
        )
        return result
    finally:
        db.close()
    


class ChunkMetadata(BaseModel):
    chunk_index: int
    chunk_hash: str
    chunk_size: int

class FileUploadInit(BaseModel):
    user_id: int
    file_name: str
    file_size: int
    num_chunks: int
    chunks: List[ChunkMetadata] # List of hashes the user calculated

@router.post("/files/init")
async def initialize_upload(payload: FileUploadInit, db: Session = Depends(get_db)):
    # A. Create the File record
    new_file = FileModel(
        user_id=payload.user_id,
        file_name=payload.file_name,
        file_size=payload.file_size,
        num_chunks=payload.num_chunks
    )
    db.add(new_file)
    db.flush() # This generates the file_id without finishing the transaction

    # B. Create the "slots" for the Chunks
    for c in payload.chunks:
        new_chunk = Chunk(
            file_id=new_file.file_id,
            chunk_index=c.chunk_index,
            chunk_hash=c.chunk_hash,
            chunk_size=c.chunk_size
        )
        db.add(new_chunk)

    db.commit() # Save everything to DB

    return {
        "status": "success",
        "file_id": new_file.file_id,
        "message": "Metadata saved. You can now start sending chunks."
    }