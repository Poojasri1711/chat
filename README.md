# Offline AI Lab Chatbot

A college-lab chatbot designed for **zero Internet at runtime**.

## Architecture

- One **HOST PC** runs the local web server and local GGUF AI model.
- Client PCs only need Chrome/Edge.
- Client PCs do **not** need Ollama, Python, Node.js, or an AI model.
- All traffic stays inside the lab LAN.

Client:
`http://HOST-IP:8000`

Flow:

Browser -> LAN -> FastAPI -> llama.cpp/llama-server -> local GGUF model -> Browser

## Important

This project intentionally does NOT use Ollama.

The host uses `llama-server.exe` from llama.cpp. The GGUF model is stored on the host.

The Internet is only needed initially to obtain the required runtime/model. After that, the chatbot can run with Internet disconnected.

## Folder layout

```text
offline-ai-lab-chatbot/
  server/
    main.py
    config.py
  frontend/
    index.html
    style.css
    app.js
  models/
    PUT_YOUR_MODEL_HERE.gguf
  runtime/
    llama-server.exe
  start.bat
  stop.bat
  requirements.txt
  README.md
```

## HOST setup

1. Install Python 3.11+ on the HOST PC.
2. Put `llama-server.exe` from llama.cpp into `runtime/`.
3. Put a compatible GGUF model into `models/`.
4. Edit `server/config.py` if your model filename is different.
5. Open Command Prompt in this folder.
6. Run:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

7. Run `start.bat`.

The script starts the local llama.cpp server and the FastAPI web server.

The console will show the LAN address, for example:

`http://192.168.1.100:8000`

## CLIENT setup

Nothing needs to be installed.

1. Connect the client PC to the same lab LAN.
2. Open Chrome/Edge.
3. Enter the host address shown by the host:

`http://192.168.1.100:8000`

Internet can be disconnected.

## Windows Firewall

The first time Windows asks whether Python should communicate on the network, allow it on **Private networks** only.

If clients cannot connect, allow TCP port 8000 on the host's Private network.

Do not expose this server to the public Internet.

## Model

Use a GGUF instruct/chat model appropriate for the host's RAM.

A smaller quantized model is recommended for an ordinary lab PC.

The model is not included in this project because model files can be several GB.

## Offline test

1. Start the host while LAN is available.
2. Connect a client to the same LAN.
3. Open the displayed URL.
4. Ask: `Explain TCP in simple English.`
5. Disconnect the lab's Internet.
6. Ask another question.
7. The answer must still be generated.

The application itself makes no cloud/API calls.

## Notes

- This is a LAN-hosted offline system, not a public website.
- A public Vercel/GitHub URL cannot work when a computer has no Internet.
- If the lab LAN itself is unavailable, the clients cannot reach the host. In that case, each PC needs a packaged standalone version.
