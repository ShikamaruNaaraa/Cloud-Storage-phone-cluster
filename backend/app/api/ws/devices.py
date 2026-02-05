from fastapi import WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from app.models.device import Device
from app.core.database import SessionLocal
from app.core.connection_manager import manager 
from app.models.chunk_replication import ChunkReplication


logger = logging.getLogger("uvicorn")

async def device_ws(ws: WebSocket):
    # 1. Accept the socket first so we can talk
    await ws.accept()
    db: Session = SessionLocal()
    current_device_id = None

    try:
        # 2. Handshake / Registration Phase 
        # We expect the first message to identify the node
        payload = await ws.receive_json()
        
        if payload.get("type") != "register": # its not register, more like attaching a ws as well with REST
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        fingerprint = payload["fingerprint"]
        
        # Look up or Create Device
        device = db.query(Device).filter(Device.device_fingerprint == fingerprint).first()

        #NOT NEEDED AS THE REGISTRATION PART IS ALREADY DONE USING REST

        # if not device:
        #     device = Device(
        #         user_id=payload["user_id"],
        #         device_name=payload["device_name"],
        #         device_fingerprint=fingerprint,
        #         storage_capacity=payload["storage_capacity"],
        #         available_storage=payload["available_storage"],
        #         status="ONLINE",
        #         last_heartbeat=datetime.utcnow()
        #     )
        #     db.add(device)
        # else:
        #     device.status = "ONLINE"
        #     device.available_storage = payload.get("available_storage", device.available_storage)
        #     device.last_heartbeat = datetime.utcnow()
        
        # db.commit()
        # db.refresh(device)

        # 2.5 Validate device existence and liveness

        # Case 1: Device does not exist (not registered via REST)
        if not device:
            await ws.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Device not registered"
            )
            return

        # Case 2: Device exists but is OFFLINE (heartbeat timed out)
        if device.status != "ONLINE":
            await ws.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="Device is offline"
            )
            return

        current_device_id = device.device_id

        # 3. Register with the Global Manager
        # This allows the Coordinator to find this socket later for commands
        await manager.connect(current_device_id, ws)

        # 4. Send ACK so the phone knows it's part of the cluster
        await ws.send_json({
            "status": "ready",
            "device_id": current_device_id,
            # "config": {"heartbeat_interval": 30} HEARTBEAT DONE USING REST
        })

        # 5. Main Control Loop
        while True:
            msg = await ws.receive_json()
            
            #heartbeat already done using rest

            # if msg["type"] == "heartbeat":
            #     # Bulk update to avoid constant DB writes if performance is an issue
            #     device.last_heartbeat = datetime.utcnow()
            #     device.available_storage = msg.get("available_storage", device.available_storage)
            #     db.commit()
            if msg["type"] == "cmd_ack":
                # Device confirms it received a  command
                print(f"Device {device.device_id} is processing {msg['task_id']}")

            elif msg["type"] == "CHUNK_STORED_SUCCESS":
                chunk_id = msg.get("chunk_id")
                
                # 1. Find the replication record for this specific device and chunk
                replication_entry = db.query(ChunkReplication).filter(
                    ChunkReplication.chunk_id == chunk_id,
                    ChunkReplication.device_id == current_device_id # device_id from the WS session
                ).first()

                if replication_entry:
                    # 2. Upgrade status to ACTIVE
                    replication_entry.replica_status = "ACTIVE"
                    db.commit()
                    print(f"Chunk {chunk_id} is now ACTIVE on Device {current_device_id}")
            

    except WebSocketDisconnect:
        logger.info(f"Device {current_device_id} disconnected.")
    except Exception as e:
        logger.error(f"Error in WS loop: {e}")
    finally:
        # 6. Cleanup - Crucial for distributed state
        if current_device_id:
            manager.disconnect(current_device_id)

            # Re-fetch device in a fresh session state if needed
            # device = db.query(Device).get(current_device_id)
            # if device:
            #     device.status = "OFFLINE"
            #     db.commit()
        db.close()