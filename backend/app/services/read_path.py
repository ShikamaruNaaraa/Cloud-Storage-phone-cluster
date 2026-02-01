#this file might not be needed anymore


# from app.models.chunk import Chunk
# from app.models.chunk_replication import ChunkReplication
# from app.models.device import Device
# from app.services.replication_monitor import ensure_replication
# from sqlalchemy.orm import Session
# import requests
# import hashlib

# def retrieve_chunk(
#         db: Session,
#         chunk
# ):
#     replicas = (
#         db.query(ChunkReplication).filter(
#             ChunkReplication.chunk_id == chunk.chunk_id,
#             ChunkReplication.replica_status == "ACTIVE"
#         ).all()
#     )

#     if not replicas:
#         raise RuntimeError(f"No ACTIVE replicas found for chunk_id {chunk.chunk_id}")
    
#     for replica in replicas:
#         device = db.query(Device).filter(
#             Device.device_id == replica.device_id,
#             Device.status == "ONLINE"            
#         ).first()

#         if not device:
#             continue

#         try:
#             response = requests.get(
#                 f"http://{device.ip_address}/chunks/{chunk.chunk_id}",
#                 timeout=5)
#             response.raise_for_status()
#             data = response.content

#             # Verify chunk integrity
#             if hashlib.sha256(data).hexdigest() != chunk.chunk_hash:    
#                 raise ValueError("Chunk hash mismatch")

#             #success
#             return data
#         except Exception:
#             replica.replica_status = "LOST"
#             db.commit()

#             ensure_replication(db, chunk.chunk_id)
#     raise RuntimeError(f"Failed to retrieve chunk_id {chunk.chunk_id} from all ACTIVE replicas")



# def retrieve_file(db, file_id):
#     chunks = (
#         db.query(Chunk)
#         .filter(Chunk.file_id == file_id)
#         .order_by(Chunk.chunk_index)
#         .all()
#     )
#     # Retrieve each chunk and collect encrypted data
    
#     encrypted_chunks = []

#     for chunk in chunks:
#         encrypted_chunks.append(retrieve_chunk(db, chunk))

#     return encrypted_chunks


