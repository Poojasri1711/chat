from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT / "frontend"
MODEL_DIR = ROOT / "models"
RUNTIME_DIR = ROOT / "runtime"

HOST = os.getenv("CHAT_HOST", "0.0.0.0")
PORT = int(os.getenv("CHAT_PORT", "8000"))

# Change this to your actual GGUF filename.
MODEL_FILE = os.getenv(
    "CHAT_MODEL",
    str(MODEL_DIR / "model.gguf")
)

# llama-server executable.
LLAMA_SERVER = os.getenv(
    "LLAMA_SERVER",
    str(RUNTIME_DIR / "llama-server.exe")
)

# Local llama.cpp server endpoint.
LLAMA_URL = os.getenv("LLAMA_URL", "http://127.0.0.1:8080")

# Adjust based on the host computer.
CONTEXT_SIZE = int(os.getenv("CHAT_CTX", "4096"))
GPU_LAYERS = int(os.getenv("CHAT_GPU_LAYERS", "0"))
