/** Tab = push-to-talk, Esc = silence Friday */
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
        // For now: notify backend that PTT ended; full STT upload can be added
        // when /voice endpoint accepts multipart. Fallback: user types.
        setState("thinking");
        console.log("[PTT] recorded", blob.size, "bytes");
        // Optional: POST blob to /voice when endpoint is ready
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

  function silence() {
    // Stop any TTS playback + cancel in-flight feel
    stopPTT();
    setState("");
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    // Best-effort: tell backend to stand down speaking
    fetch(API + "/health").catch(() => {});
    const stream = document.getElementById("stream");
    if (stream) {
      const d = document.createElement("div");
      d.className = "msg friday";
      d.innerHTML = '<span class="tag">FRIDAY</span>Standing by.';
      stream.appendChild(d);
      stream.scrollTop = stream.scrollHeight;
    }
  }

  window.addEventListener("keydown", (e) => {
    if (e.code === "Tab" && !e.repeat && e.target.tagName !== "INPUT") {
      e.preventDefault();
      startPTT();
    }
    if (e.code === "Escape") {
      e.preventDefault();
      silence();
    }
  });

  window.addEventListener("keyup", (e) => {
    if (e.code === "Tab") {
      e.preventDefault();
      stopPTT();
    }
  });

  console.log("[Friday] Hotkeys: Tab = push-to-talk, Esc = silence");
})();
