from app.core.database import SessionLocal
from app.services.heartbeat import handle_heartbeat
from app.models.user import User


def main():
    db = SessionLocal()
    try:
        handle_heartbeat(db, device_id=1)
        print("Heartbeat updated")
    finally:
        db.close()

if __name__ == "__main__":
    main()
