(() => {
  if (!window.taskflowProjectId) return;
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${scheme}://${window.location.host}/ws/projects/${window.taskflowProjectId}/`);
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      const toast = document.createElement("div");
      toast.className = "flash";
      toast.textContent = data.message + " Refreshing board…";
      document.querySelector(".content")?.prepend(toast);
      setTimeout(() => window.location.reload(), 1100);
    } catch (e) { console.error("TaskFlow update error", e); }
  };
  socket.onclose = () => console.info("TaskFlow live connection closed.");
  socket.onerror = () => console.info("TaskFlow live connection unavailable.");
})();
