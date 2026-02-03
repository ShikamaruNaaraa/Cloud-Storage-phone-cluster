from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.device import Device

HEARTBEAT_TIMEOUT = timedelta(seconds=13)

def mark_offline_devices(db: Session):
    cutoff = datetime.now(timezone.utc) - HEARTBEAT_TIMEOUT

    devices = (
        db.query(Device)
        .filter(Device.last_heartbeat < cutoff)
        .filter(Device.status == "ONLINE")
        .all()
    )

    for device in devices:
        print(f"Marking device {device.device_id} as OFFLINE")
        device.status = "OFFLINE"

    if devices:
        db.commit()
