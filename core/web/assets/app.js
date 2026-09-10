async function loadStatus() {
  const status = document.getElementById("status");
  const error = document.getElementById("error");
  try {
    const response = await fetch("/api/v1/health", { credentials: "same-origin" });
    if (!response.ok) throw new Error("health request failed");
    const health = await response.json();
    status.textContent = JSON.stringify(health, null, 2);
  } catch (_error) {
    error.hidden = false;
    error.textContent = "The local Control API is unavailable.";
    status.textContent = "Unavailable";
  }
}

loadStatus();
