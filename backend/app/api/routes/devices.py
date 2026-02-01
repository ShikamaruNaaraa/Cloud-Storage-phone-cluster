from app.core.database import SessionLocal
from sqlalchemy.orm import Session 
from app.services.registration import register_device
from app.models.chunk import Chunk
from app.models.device import Device
from fastapi import APIRouter, Depends, HTTPException
from app.models.file import File as FileModel   # Avoid name conflict with fastapi 'File'
from app.models.chunk import Chunk             
from pydantic import BaseModel
from typing import List
from app.core.database import get_db

router = APIRouter()

@router.post("/devices/register")
def register_device_endpoint(payload: dict, db: Session = Depends(get_db)):
    result = register_device(
        db=db,
        user_id=payload["user_id"],
        device_name=payload["device_name"],
        storage_capacity=payload["storage_capacity"],
        available_storage=payload["available_storage"],
        fingerprint=payload["fingerprint"],
    )
    return result
    

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

# File upload initialization endpoint:
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


from fastapi import UploadFile, File
import os

TEMP_STORAGE_PATH = "./temp_chunks"
os.makedirs(TEMP_STORAGE_PATH, exist_ok=True)

@router.post("/files/{file_id}/upload-data")
async def upload_file_data(
    file_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 1. Verify the file exists in DB
    db_file = db.query(FileModel).filter(FileModel.file_id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # 2. Read the binary content
    content = await file.read()
    
    # 3. Slice and Save Chunks locally
    # We calculate size. (Total size / num_chunks)
    chunk_size = len(content) // db_file.num_chunks
    
    for i in range(db_file.num_chunks):
        start = i * chunk_size
        end = start + chunk_size if i < db_file.num_chunks - 1 else len(content)
        chunk_data = content[start:end]
        
        # Save to disk so phones can download it later
        # Find the chunk_id from DB for this index
        db_chunk = db.query(Chunk).filter(
            Chunk.file_id == file_id, 
            Chunk.chunk_index == i
        ).first()

        with open(f"{TEMP_STORAGE_PATH}/chunk_{db_chunk.chunk_id}.bin", "wb") as f:
            f.write(chunk_data)

    return {"status": "success", "message": "Chunks prepared on server."}