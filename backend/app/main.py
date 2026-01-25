from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws/node")
async def node_ws(ws: WebSocket, device_id: str, device_name: str, available_space: int, storage_capacity: int):
    await ws.accept()
    try:    
        while True:
            msg = await ws.receive_json()
            msg_type = msg.get("type")

            if msg_type == "register":
                device_id = msg.get("device_id")
                device_name = msg.get("device_name")
                available_space = msg.get("available_space")
                storage_capacity = msg.get("storage_capacity")
                
                now = datetime.utcnow()

                #upsert in db
                print(f"Registered node {device_id} - {device_name}")
            
            elif msg_type == "heartbeat":
                device_id = msg.get("device_id")
                now = datetime.utcnow()
                # update last seen in db
                print(f"Heartbeat from {device_id} at {now}")
            elif msg_type == "store_chunk":
                chunk_id = msg.get("chunk_id")
                file_id = msg.get("file_id")
                size = msg.get("size")
                # store chunk metadata in db
                print(f"Storing chunk {chunk_id} for file {file_id}")
            # register, heartbeat, store/retrieve commands

@app.post("/upload")
async def upload_file():
    # receive encrypted chunks + metadata
    # decide replication
    return {"status": "uploaded"}

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    # locate chunks
    # request from storage nodes
    return {"status": "ready"}

@app.get("/status")
async def status():
    return {
        "nodes_alive": 4,
        "storage_used": "10GB"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
