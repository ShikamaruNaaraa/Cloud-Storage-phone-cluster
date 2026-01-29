from app.models.device import Device
from app.models.chunk_replication import ChunkReplication

def plan_replication(
    db,
    chunk_id: int,
    chunk_size: int,
    replicas: int = 2,
):
    # Find existing (non-lost) replicas
    existing_device_ids = {
        r.device_id
        for r in db.query(ChunkReplication)
        .filter(
            ChunkReplication.chunk_id == chunk_id,
            ChunkReplication.replica_status != "LOST"
        )
        .all()
    }

    needed = replicas - len(existing_device_ids)
    if needed <= 0:
        return

    # Find candidate devices
    candidates = (
        db.query(Device)
        .filter(
            Device.status == "ONLINE",
            Device.available_storage >= chunk_size,
            ~Device.device_id.in_(existing_device_ids),
        )
        .order_by(Device.available_storage.desc())
        .limit(needed)
        .all()
    )

    # Create replication entries
    for device in candidates:
        db.add(
            ChunkReplication(
                chunk_id=chunk_id,
                device_id=device.device_id,
                replica_status="REPLICATING",
            )
        )

    db.commit()
