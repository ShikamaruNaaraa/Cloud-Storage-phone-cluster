from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.device import Device

HEARTBEAT_TIMEOUT = timedelta(seconds=30)

def mark_offline_devices(db: Session):
    cutoff = datetime.now(timezone.utc) - HEARTBEAT_TIMEOUT

    devices = (
        db.query(Device)
        .filter(Device.last_heartbeat < cutoff)
        .filter(Device.status == "ONLINE")
        .all()
    )

    for device in devices:
        device.status = "OFFLINE"

    if devices:
        db.commit()
