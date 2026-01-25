from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.user import User

def handle_heartbeat(db: Session, device_id: int):
    device = db.query(Device).filter(Device.device_id == device_id).first()

    if device is None:
        raise ValueError("Device not registered")

    device.last_heartbeat = datetime.now(timezone.utc)
    device.status = "ONLINE"

    db.commit()
    print(f"Heartbeat updated for device {device_id} at {device.last_heartbeat}")


