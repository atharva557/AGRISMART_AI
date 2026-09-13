// app/static/js/assistant.js
// Drives the Farmer Assistant widget (_assistant_widget.html):
//   - fetches a grounded, plain-language explanation on load
//   - runs a text chat against /api/assistant/chat
//
// Requires `window.detectionContext` to be set by the page that includes
// this widget (see comment at top of _assistant_widget.html).

(function () {
  const sessionId = "session-" + Math.random().toString(36).slice(2);
  let currentLang = "en";

  const explanationEl = document.getElementById("assistant-explanation");
  const chatLog = document.getElementById("assistant-chat-log");
  const chatForm = document.getElementById("assistant-chat-form");
  const chatInput = document.getElementById("assistant-input");
  const langSelect = document.getElementById("assistant-lang");

  function getContext() {
    return window.detectionContext || {};
  }

  function appendMessage(role, text) {
    const div = document.createElement("div");
    div.className = "assistant-msg assistant-msg-" + role;
    div.textContent = (role === "user" ? "You: " : "Assistant: ") + text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  async function loadExplanation() {
    const ctx = getContext();
    if (!ctx.disease_label) {
      explanationEl.textContent = "No detection result available yet.";
      return;
    }
    explanationEl.textContent = "Loading explanation…";
    try {
      const res = await fetch("/api/assistant/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...ctx, lang: currentLang }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      explanationEl.innerText = data.explanation;
      window.__assistantContext = data.context; // reuse for chat calls
    } catch (err) {
      explanationEl.textContent = "Could not load explanation: " + err.message;
    }
  }

  async function sendChat(message) {
    appendMessage("user", message);
    try {
      const res = await fetch("/api/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message,
          context: window.__assistantContext || getContext(),
          lang: currentLang,
        }),
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      appendMessage("assistant", data.reply);
    } catch (err) {
      appendMessage("assistant", "Sorry, I couldn't answer that: " + err.message);
    }
  }

  // --- events ---
  langSelect.addEventListener("change", (e) => {
    currentLang = e.target.value;
    loadExplanation();
  });

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    chatInput.value = "";
    sendChat(msg);
  });

  // init
  document.addEventListener("DOMContentLoaded", loadExplanation);
  if (document.readyState !== "loading") loadExplanation();
})();
