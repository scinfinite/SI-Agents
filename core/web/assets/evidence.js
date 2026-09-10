function node(tag, text, className) {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = String(text);
  if (className) item.className = className;
  return item;
}
function clear(item) { while (item.firstChild) item.removeChild(item.firstChild); }
function card(title, value, detail) {
  const article = node("article", undefined, "card metric");
  article.append(node("p", title, "label"), node("strong", value, "metric-value"), node("p", detail, "muted"));
  return article;
}
async function loadEvidence() {
  const error = document.getElementById("error"); error.hidden = true; clear(document.getElementById("summary")); clear(document.getElementById("records"));
  try {
    const runId = document.getElementById("run-id").value.trim();
    const path = runId ? `/api/v1/runs/${encodeURIComponent(runId)}/timeline` : "/api/v1/evidence/records";
    const response = await fetch(path, { credentials: "same-origin", cache: "no-store", headers: { "Accept": "application/json" } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const records = runId ? (data.events || []) : data;
    const counts = runId ? data.counts : {
      total: records.length,
      facts: records.filter((x) => x.kind === "fact").length,
      observations: records.filter((x) => x.kind === "observation").length,
      inferences: records.filter((x) => x.kind === "inference").length,
      uncertainties: records.filter((x) => x.kind === "uncertainty").length,
      verified: records.filter((x) => x.verification === "verified").length,
      contradicted: records.filter((x) => x.verification === "contradicted").length
    };
    const summary = document.getElementById("summary");
    summary.append(card("Records", counts.total, runId ? "timeline evidence" : "persisted evidence"), card("Verified", counts.verified, "verification state"), card("Contradicted", counts.contradicted, "requires attention"), card("Uncertainty", counts.uncertainties, "explicit unknowns"));
    const wrap = node("div", undefined, "table-wrap"); const table = node("table"); const head = node("tr");
    ["Claim", "Kind", "Confidence", "Verification", "Source", "Run", "Provenance"].forEach((label) => head.append(node("th", label))); table.append(node("thead")); table.querySelector("thead").append(head);
    const body = node("tbody"); records.forEach((record) => { const row = node("tr"); [record.claim, record.kind, Number(record.confidence).toFixed(2), record.verification, record.source, record.run_id || "—", (record.provenance || []).join(" → ") || "—"].forEach((value) => row.append(node("td", value))); body.append(row); }); table.append(body); wrap.append(table); document.getElementById("records").append(wrap);
  } catch (err) {
    error.hidden = false; error.textContent = "Evidence could not be loaded.";
  }
}
document.getElementById("refresh").addEventListener("click", loadEvidence);
document.getElementById("run-id").addEventListener("keydown", (event) => { if (event.key === "Enter") loadEvidence(); });
loadEvidence();
