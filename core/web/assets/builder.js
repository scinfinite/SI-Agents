const fields = ["id", "name", "division", "base_agent_id", "description", "responsibilities", "deliverables", "success_criteria", "boundaries", "skills", "capabilities", "permissions", "harnesses", "environments"];
const $ = (id) => document.getElementById(id);

function lines(id) {
  return $(id).value.split("\n").map((x) => x.trim()).filter(Boolean);
}
function payload() {
  const value = {};
  fields.forEach((id) => { value[id] = id === "base_agent_id" ? $(id).value.trim() || null : $(id).value; });
  ["responsibilities", "deliverables", "success_criteria", "boundaries", "skills", "capabilities", "permissions", "harnesses", "environments"].forEach((id) => { value[id] = lines(id); });
  return value;
}
async function post(path, body) {
  const response = await fetch(path, { method: "POST", credentials: "same-origin", cache: "no-store", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(body) });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || `HTTP ${response.status}`);
  return data;
}
function show(result) {
  const box = $("result"); box.textContent = result.valid ? "Valid: ready as a non-executing authoring artifact." : `Invalid: ${result.errors.join("; ")}`;
  $("markdown").textContent = result.markdown || "";
}
async function validate() {
  try { show(await post("/api/v1/agent-builder/validate", payload())); } catch (error) { $("result").textContent = error.message; }
}
async function save(event) {
  event.preventDefault();
  try { const result = await post("/api/v1/agent-builder/drafts", payload()); show({ valid: true, errors: [], warnings: [], agent: result, markdown: "Saved valid draft. Use Test to revalidate it." }); await loadDrafts(); }
  catch (error) { $("result").textContent = error.message; }
}
async function loadBase() {
  const id = $("base_agent_id").value.trim(); if (!id) { $("result").textContent = "Enter a canonical base agent ID first."; return; }
  try { const response = await fetch(`/api/v1/agent-builder/from/${encodeURIComponent(id)}`, { cache: "no-store" }); const data = await response.json(); if (!response.ok) throw new Error("Base agent not found"); fields.forEach((field) => { if (field in data && field !== "base_agent_id") $(field).value = Array.isArray(data[field]) ? data[field].join("\n") : (data[field] ?? ""); }); $("base_agent_id").value = data.base_agent_id || id; await validate(); }
  catch (error) { $("result").textContent = error.message; }
}
async function loadDrafts() {
  try { const response = await fetch("/api/v1/agent-builder", { cache: "no-store" }); const drafts = await response.json(); const box = $("drafts"); box.textContent = ""; drafts.forEach((draft) => { const row = document.createElement("div"); row.className = "draft-row"; const title = document.createElement("strong"); title.textContent = `${draft.name} · ${draft.status}`; const detail = document.createElement("span"); detail.textContent = ` ${draft.id} · revision ${draft.revision}`; row.append(title, detail); const test = document.createElement("button"); test.type = "button"; test.className = "button"; test.textContent = "Test"; test.addEventListener("click", async () => { try { show(await post(`/api/v1/agent-builder/drafts/${encodeURIComponent(draft.id)}/test`, {})); } catch (error) { $("result").textContent = error.message; } }); row.append(test); box.append(row); }); }
  catch (error) { $("drafts").textContent = error.message; }
}
$("validate").addEventListener("click", validate);
$("load-base").addEventListener("click", loadBase);
$("builder-form").addEventListener("submit", save);
loadDrafts();
