import os
import uuid
import shutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# AI Generated Starts here
import tempfile
from datetime import datetime, timezone

# 1. Store in /tmp/uploads on Linux (Render) or tempdir on Windows
UPLOAD_DIR = "/tmp/uploads" if os.name != "nt" else os.path.join(tempfile.gettempdir(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount /images (and /uploads for backwards compatibility)
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
async def root():
    return {"message": "FastAPI WebSocket chat server is running"}


# 2. HTTP POST route /upload-photo (multipart/form-data)
@app.post("/upload-photo")
@app.post("/upload")
async def upload_photo(file: UploadFile = File(...)):
    # Extract extension (e.g. .jpg, .png)
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save incoming image to disk (/tmp/uploads)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": unique_filename,
        "url": f"/images/{unique_filename}",
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }

# AI Generated ends here, rest is from the websocket mob08 activity


# 3. WebSocket Connection Manager (remains the same)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception as e:
                print("Error sending to a client:", e)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from client: {data}")
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print("Unexpected error in websocket:", e)
        manager.disconnect(websocket)
        try:
            await websocket.close()
        except:
            pass
