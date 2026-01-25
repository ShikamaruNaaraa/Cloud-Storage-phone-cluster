from fastapi import WebSocket, WebSocketDisconnect
from app.core.database import SessionLocal
from app.services.heartbeat import handle_heartbeat
import app.models  # ensure models registered
import json
import traceback

async def device_ws(websocket: WebSocket):
    await websocket.accept()
    print("WS accepted")

    try:
        while True:
            data = await websocket.receive_json()
            print("Received:", data)

            device_id = data.get("device_id")
            if device_id is None:
                await websocket.send_json({"error": "device_id required"})
                continue

            db = SessionLocal()
            try:
                handle_heartbeat(db, device_id)
            except Exception as e:
                db.rollback()
                traceback.print_exc()
                await websocket.send_json({"error": str(e)})
            finally:
                db.close()

            await websocket.send_json({"status": "ok"})

    except WebSocketDisconnect:
        print("WS disconnected cleanly")

    except Exception:
        # THIS is what was missing
        traceback.print_exc()
        await websocket.close()
