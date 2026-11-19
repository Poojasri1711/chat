const messagesEl = document.getElementById("messages");
const form = document.getElementById("chatForm");
const input = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const statusEl = document.getElementById("status");
const serverInfo = document.getElementById("serverInfo");
const clearBtn = document.getElementById("clearBtn");
const newChat = document.getElementById("newChat");

let messages = [];
let busy = false;

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `msg ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return bubble;
}

function resetUI() {
  messagesEl.innerHTML = `
    <div class="welcome">
      <h2>Offline AI Assistant</h2>
      <p>This chatbot communicates only with the local lab server.</p>
      <p>Internet is not required once the host is running.</p>
    </div>`;
}

async function checkStatus() {
  try {
    const r = await fetch("/api/status", {cache:"no-store"});
    const data = await r.json();
    statusEl.textContent = data.ai === "online"
      ? "🟢 Connected to Offline AI Server"
      : "🔴 Server online, AI engine unavailable";
    serverInfo.textContent = `${data.url} · AI: ${data.ai}`;
  } catch {
    statusEl.textContent = "🔴 Cannot reach Offline AI Server";
    serverInfo.textContent = "Server unavailable";
  }
}

async function sendChat() {
  const text = input.value.trim();
  if (!text || busy) return;

  if (messagesEl.querySelector(".welcome")) resetUI();

  messages.push({role:"user", content:text});
  addMessage("user", text);
  input.value = "";

  const bubble = addMessage("assistant", "");
  messages.push({role:"assistant", content:""});
  busy = true;
  sendBtn.disabled = true;
  sendBtn.textContent = "Generating...";

  try {
    const r = await fetch("/api/chat", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({
        messages,
        temperature:0.7,
        max_tokens:512
      })
    });

    if (!r.ok) throw new Error(`HTTP ${r.status}`);

    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const {value, done} = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, {stream:true});

      const lines = buffer.split("\n");
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        const raw = line.slice(5).trim();
        if (!raw || raw === "[DONE]") continue;

        try {
          const data = JSON.parse(raw);
          if (data.error) throw new Error(data.error);

          const delta = data.choices?.[0]?.delta?.content || "";
          if (delta) {
            bubble.textContent += delta;
            messages[messages.length - 1].content += delta;
            messagesEl.scrollTop = messagesEl.scrollHeight;
          }
        } catch (e) {
          if (e.message) throw e;
        }
      }
    }
  } catch (err) {
    bubble.textContent = "Error: " + err.message;
    bubble.classList.add("error");
    messages.pop();
  } finally {
    busy = false;
    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
    checkStatus();
  }
}

form.addEventListener("submit", e => {
  e.preventDefault();
  sendChat();
});

input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendChat();
  }
});

clearBtn.addEventListener("click", () => {
  messages = [];
  resetUI();
});

newChat.addEventListener("click", () => {
  messages = [];
  resetUI();
  input.focus();
});

checkStatus();
setInterval(checkStatus, 10000);
