"use strict";
const $ = (id) => document.getElementById(id);
const lines = (id) => $(id).value.split(/\r?\n/).map((x) => x.trim()).filter(Boolean);
function render(data) {
  $("targets-list").textContent = data.targets.length ? data.targets.map((x) => `${x.id} — ${x.version} — ${x.adapter_path}`).join("\n") : "No registered harness targets.";
  $("plans-list").textContent = data.plans.length ? data.plans.map((x) => `${x.id} — ${x.harness_id} — ${x.state}${x.reasons.length ? ` — ${x.reasons.join("; ")}` : ""}`).join("\n") : "No deployment plans.";
}
async function refresh() {
  const response = await fetch("/api/v1/deployments", {cache: "no-store"});
  if (!response.ok) throw new Error("Unable to load deployment state");
  render(await response.json());
}
$("plan-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {id: $("plan-id").value.trim(), harness_id: $("harness-id").value.trim(), agents: lines("agents"), teams: lines("teams"), skills: lines("skills")};
  try {
    const response = await fetch("/api/v1/deployments", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
    const data = await response.json();
    $("result").textContent = JSON.stringify(data, null, 2);
    await refresh();
  } catch (error) { $("result").textContent = String(error); }
});
refresh().catch((error) => { $("targets-list").textContent = String(error); $("plans-list").textContent = "Unavailable"; });
