import asyncio
from app.models.chunk_replication import ChunkReplication
from app.services.plan_replication import plan_replication

# MUST include http:// or the phone's request will fail
SERVER_IP = "http://192.168.1.50:8000"  

async def distribute_chunk(db, chunk, manager):
    # 1. Plan the replication (This adds rows to ChunkReplication)
    plan_replication(db, chunk.chunk_id, chunk.chunk_size)
    
    # 2. Re-fetch from DB to ensure we have the newly created rows
    # We filter by 'REPLICATING' to target only the new ones
    new_assignments = db.query(ChunkReplication).filter(
        ChunkReplication.chunk_id == chunk.chunk_id,
        ChunkReplication.replica_status == "REPLICATING"
    ).all()

    if not new_assignments:
        print(f"No devices available to replicate chunk {chunk.chunk_id}")
        return

    # 3. Create a list of tasks to send commands in parallel
    tasks = []
    for assignment in new_assignments:
        tasks.append(
            manager.send_command(
                device_id=assignment.device_id,
                command_type="DOWNLOAD_CHUNK",
                data={
                    "chunk_id": chunk.chunk_id,
                    "download_url": f"{SERVER_IP}/chunks/download/{chunk.chunk_id}",
                    "expected_hash": chunk.chunk_hash
                }
            )
        )
    
    # Send all commands at once instead of one-by-one
    await asyncio.gather(*tasks)