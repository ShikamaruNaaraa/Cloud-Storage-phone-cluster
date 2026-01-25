from app.core.database import SessionLocal
from app.services.offline_detection import mark_offline_devices
from app.models.device import Device
from app.models.user import User

def main():
    db = SessionLocal()
    try:
        mark_offline_devices(db)
        print("Offline detection ran")
    finally:
        db.close()

if __name__ == "__main__":
    main()
