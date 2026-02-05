from app.api.routes.ws_devices import manager  # the singleton manager
from app.models.chunk_replication import ChunkReplication

async def dispatch_replication_to_devices(db, chunk_id: int, server_base_url: str):
    reps = (
        db.query(ChunkReplication)
        .filter(
            ChunkReplication.chunk_id == chunk_id,
            ChunkReplication.replica_status == "REPLICATING",
        )
        .all()
    )

    for r in reps:
        payload = {
            "type": "replicate_chunk",
            "chunk_id": chunk_id,
            "download_url": f"{server_base_url.rstrip('/')}/chunks/{chunk_id}/download",
        }

        ok = await manager.send_json_to_device(r.device_id, payload)

        if not ok:
            # device not connected via WS right now
            r.replica_status = "PENDING"  # or OFFLINE / QUEUED

    db.commit()
