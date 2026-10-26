/** Tab = push-to-talk (hold). Esc = FULL SHUTDOWN (quit Friday). */
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

  async function startPTT() {
    if (recording) return;
    recording = true;
    setState("listening");
    chunks = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunks, { type: "audio/webm" });
        setState("thinking");
        console.log("[PTT] recorded", blob.size, "bytes");
        setState("");
      };
      mediaRecorder.start();
    } catch (e) {
      console.error("Mic error", e);
      setState("");
      recording = false;
    }
  }

  function stopPTT() {
    if (!recording || !mediaRecorder) return;
    recording = false;
    try { mediaRecorder.stop(); } catch (_) {}
  }

  /** Full shutdown: stop voice, stand down live, kill backend, close UI */
  async function shutdown() {
    stopPTT();
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    setState("");

    const streamEl = document.getElementById("stream");
    if (streamEl) {
      const d = document.createElement("div");
      d.className = "msg friday";
      d.innerHTML = '<span class="tag">FRIDAY</span>Shutting down.';
      streamEl.appendChild(d);
    }

    // Ask backend to stand down + exit
    try {
      await fetch(API + "/shutdown", { method: "POST" });
    } catch (_) {}

    // Close window (works in Tauri and most desktop webviews)
    try {
      if (window.__TAURI__) {
        const { getCurrentWindow } = await import("@tauri-apps/api/window");
        await getCurrentWindow().close();
      } else {
        window.close();
      }
    } catch (_) {
      // Last resort: blank the page so it's obvious she's off
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

  console.log("[Friday] Tab = talk · Esc = SHUT DOWN");
})();
