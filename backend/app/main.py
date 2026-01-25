from fastapi import FastAPI, WebSocket
from app.api.ws.devices import device_ws

app = FastAPI()

@app.websocket("/ws/device")
async def ws_service(websocket : WebSocket):
    await device_ws(websocket)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
