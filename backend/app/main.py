from fastapi import FastAPI, WebSocket
from app.api.ws.devices import device_ws
import asyncio
from contextlib import asynccontextmanager
from app.core.scheduler import offline_monitor_loop
from app.api.routes.devices import router as device_router
from app.api.routes import chunks
from app.api.routes import ws_devices


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    task = asyncio.create_task(offline_monitor_loop())
    print("Startup: Offline monitor loop started.")
    
    yield  # The application runs while stuck here
    
    # This runs when the server stops
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Shutdown: Offline monitor loop stopped.")


app = FastAPI(lifespan=lifespan)
app.include_router(device_router)
app.include_router(chunks.router)
app.include_router(ws_devices.router)

@app.websocket("/ws/device")
async def ws_service(websocket : WebSocket):
    await device_ws(websocket)
    