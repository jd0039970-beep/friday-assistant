/** Tab = push-to-talk (hold → STT → agent). Esc = FULL SHUTDOWN. */
(function () {
  const API = "http://127.0.0.1:8787";
  let recording = false;
  let mediaRecorder = null;
  let chunks = [];

  function setState(s) {
    document.body.className = s || "";
    const sub = document.getElementById("statusSub");
    if (sub) {
      sub.textContent = ({ listening: "LISTENING", thinking: "PROCESSING", speaking: "SPEAKING", live: "LIVE MODE" }[s] || "STANDBY");
    }
  }

  function addMsg(role, text) {
    const stream = document.getElementById("stream");
    if (!stream) return;
    const d = document.createElement("div");
    d.className = "msg " + role;
    if (role === "friday") d.innerHTML = `<span class="tag">FRIDAY</span>${text}`;
    else d.textContent = text;
    stream.appendChild(d);
    stream.scrollTop = stream.scrollHeight;
  }

  async function startPTT() {
    if (recording) return;
    recording = true;
    setState("listening");
    chunks = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunks, { type: "audio/webm" });
        if (blob.size < 500) {
          setState("");
          addMsg("friday", "Too short — hold Tab a bit longer.");
          return;
        }
        setState("thinking");
        try {
          const fd = new FormData();
          fd.append("file", blob, "ptt.webm");
          const r = await fetch(API + "/voice", { method: "POST", body: fd });
          const data = await r.json();
          if (data.transcript) addMsg("user", data.transcript);
          addMsg("friday", data.reply || "(no reply)");
          const modeLabel = document.getElementById("modeLabel");
          if (modeLabel) modeLabel.textContent = data.sandbox_state || "SANDBOX";
          if (String(data.sandbox_state || "").startsWith("LIVE")) setState("live");
          else setState("");
        } catch (e) {
          setState("");
          addMsg("friday", "Voice link failed. Is the backend running?");
        }
      };
      mediaRecorder.start();
    } catch (e) {
      console.error("Mic error", e);
      setState("");
      recording = false;
      addMsg("friday", "Microphone unavailable. Allow mic access or type instead.");
    }
  }

  function stopPTT() {
    if (!recording || !mediaRecorder) return;
    recording = false;
    try { mediaRecorder.stop(); } catch (_) {}
  }

  async function shutdown() {
    stopPTT();
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    setState("");
    addMsg("friday", "Shutting down.");
    try { await fetch(API + "/shutdown", { method: "POST" }); } catch (_) {}
    try {
      if (window.__TAURI__) {
        const { getCurrentWindow } = await import("@tauri-apps/api/window");
        await getCurrentWindow().close();
      } else {
        window.close();
      }
    } catch (_) {
      document.body.innerHTML =
        '<div style="height:100vh;display:flex;align-items:center;justify-content:center;background:#02060c;color:#3fd0ff;font-family:Orbitron,sans-serif;letter-spacing:.2em">FRIDAY OFFLINE</div>';
    }
  }

  window.addEventListener("keydown", (e) => {
    if (e.code === "Tab" && !e.repeat && e.target.tagName !== "INPUT") {
      e.preventDefault();
      startPTT();
    }
    if (e.code === "Escape") {
      e.preventDefault();
      shutdown();
    }
  });

  window.addEventListener("keyup", (e) => {
    if (e.code === "Tab") {
      e.preventDefault();
      stopPTT();
    }
  });

  console.log("[Friday] Tab = talk (STT) · Esc = SHUT DOWN");
})();
