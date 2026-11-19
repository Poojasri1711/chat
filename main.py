import asyncio
import json
import os
import socket
import subprocess
import threading
from pathlib import Path
from typing import AsyncGenerator

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import (
    CONTEXT_SIZE,
    FRONTEND_DIR,
    GPU_LAYERS,
    HOST,
    LLAMA_SERVER,
    LLAMA_URL,
    MODEL_FILE,
    PORT,
)

app = FastAPI(title="Offline AI Lab Chatbot")

_llama_process = None
_process_lock = threading.Lock()


class ChatRequest(BaseModel):
    messages: list[dict]
    temperature: float = 0.7
    max_tokens: int = 512


def lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No packet needs to be sent successfully; this selects the LAN interface.
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def start_llama():
    global _llama_process

    with _process_lock:
        if _llama_process and _llama_process.poll() is None:
            return

        if not Path(LLAMA_SERVER).exists():
            raise RuntimeError(
                f"Missing llama-server executable: {LLAMA_SERVER}"
            )

        if not Path(MODEL_FILE).exists():
            raise RuntimeError(
                f"Missing GGUF model: {MODEL_FILE}"
            )

        cmd = [
            LLAMA_SERVER,
            "-m", MODEL_FILE,
            "--host", "127.0.0.1",
            "--port", "8080",
            "-c", str(CONTEXT_SIZE),
            "-ngl", str(GPU_LAYERS),
        ]

        _llama_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )


@app.on_event("startup")
async def startup():
    try:
        start_llama()
    except Exception as exc:
        print(f"[AI startup warning] {exc}")


@app.on_event("shutdown")
def shutdown():
    global _llama_process
    if _llama_process and _llama_process.poll() is None:
        _llama_process.terminate()


@app.get("/")
async def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/status")
async def status():
    llama_ok = False
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            r = await client.get(f"{LLAMA_URL}/health")
            llama_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "server": "online",
        "ai": "online" if llama_ok else "offline",
        "host": lan_ip(),
        "port": PORT,
        "url": f"http://{lan_ip()}:{PORT}",
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    # llama.cpp's OpenAI-compatible endpoint is local only.
    payload = {
        "messages": req.messages,
        "temperature": req.temperature,
        "max_tokens": req.max_tokens,
        "stream": True,
    }

    async def stream() -> AsyncGenerator[bytes, None]:
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{LLAMA_URL}/v1/chat/completions",
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        body = await response.aread()
                        yield f"data: {json.dumps({'error': body.decode(errors='replace')})}\n\n".encode()
                        return

                    async for line in response.aiter_lines():
                        if line:
                            yield (line + "\n").encode()
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n".encode()

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
