const NAV = [
  ["overview", "Overview"], ["agents", "Agents"], ["teams", "Teams"], ["workflows", "Workflows"],
  ["visualization", "Visual Organization"], ["skills", "Skills"], ["memory", "Memory"], ["knowledge", "Knowledge"], ["evidence", "Evidence"],
  ["runs", "Runs"], ["organization", "Organization"], ["governance", "Governance"],
  ["environments", "Environments"], ["harnesses", "Harnesses"], ["settings", "Settings"]
];

const ENDPOINTS = {
  agents: "/api/v1/agents", teams: "/api/v1/teams", workflows: "/api/v1/workflows",
  visualization: "/api/v1/visualization", skills: "/api/v1/skills", memory: "/api/v1/memory", knowledge: "/api/v1/memory",
  evidence: "/api/v1/evidence", runs: "/api/v1/runs", organization: "/api/v1/organization",
  governance: "/api/v1/governance", environments: "/api/v1/environments", harnesses: "/api/v1/harnesses",
  settings: "/api/v1/settings", overview: "/api/v1"
};

const DESCRIPTIONS = {
  overview: "Operational summary and live control-plane counts.", agents: "Canonical SI specialist catalog.",
  teams: "Operating teams and their declared tasks.", workflows: "Evidence-gated workflow definitions and dependencies.",
  visualization: "Interactive, read-only organization, workflow, and capability relationship maps.",
  skills: "Portable Skill artifacts visible to the control plane.", memory: "Scoped Memory read model.",
  knowledge: "Knowledge surface currently backed by the Memory read model.", evidence: "Verifiable control-plane evidence; execution evidence stays downstream.",
  runs: "Governed run records. Creation is queued-only.", organization: "Teams, divisions, assignments, and workflow topology.",
  governance: "Permissions, policies, capabilities, and risk controls.", environments: "Sanitized runtime context and supported environments.",
  harnesses: "Registered adapter families; no runtime health is inferred.", settings: "Effective Control Center and security boundary."
};

const state = { cache: {}, loading: false, graph: { mode: "organization", scale: 1, x: 0, y: 0, drag: null } };
const $ = (id) => document.getElementById(id);
const SVG_NS = "http://www.w3.org/2000/svg";

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = String(text);
  if (className) node.className = className;
  return node;
}
function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
function card(title, value, detail) {
  const article = el("article", undefined, "card metric");
  article.append(el("p", title, "label"), el("strong", value, "metric-value"), el("p", detail, "muted"));
  return article;
}
function table(headers, rows) {
  const wrap = el("div", undefined, "table-wrap"); const t = el("table");
  const thead = el("thead"); const hr = el("tr"); headers.forEach((h) => hr.append(el("th", h))); thead.append(hr); t.append(thead);
  const tbody = el("tbody"); rows.forEach((row) => { const tr = el("tr"); row.forEach((cell) => tr.append(el("td", cell))); tbody.append(tr); });
  t.append(tbody); wrap.append(t); return wrap;
}
async function get(path) {
  const response = await fetch(path, { credentials: "same-origin", cache: "no-store", headers: { "Accept": "application/json" } });
  if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json();
}
function renderNav(active) {
  const nav = $("nav"); clear(nav);
  NAV.forEach(([id, label]) => {
    const button = el("button", label, `nav-item${id === active ? " active" : ""}`); button.type = "button"; button.dataset.view = id;
    button.addEventListener("click", () => { history.pushState({}, "", `#${id}`); render(id); }); nav.append(button);
  });
}
function setConnection(ok) { $("connection-dot").className = `dot ${ok ? "ok" : "bad"}`; $("connection-text").textContent = ok ? "Control API online" : "Control API unavailable"; }
function renderOverview(data) {
  const counts = Object.fromEntries(data.counts || []); const grid = el("div", undefined, "metric-grid");
  grid.append(card("Agents", counts.agents || 0, "canonical personas"), card("Teams", counts.teams || 0, "operating teams"), card("Workflows", counts.workflows || 0, "declared workflows"), card("Runs", counts.runs || 0, "queued/control records"), card("Events", counts.events || 0, "control-plane events"));
  $("view").append(grid); const panel = el("article", undefined, "card");
  panel.append(el("h2", "Authority boundary"), el("p", "The Control Center is a view over the versioned Control API. It does not execute agents, tools, workflows, shell commands, or external calls.")); $("view").append(panel);
}
function renderAgents(data) { $("view").append(table(["Agent", "Division", "Status", "ID"], data.slice(0, 500).map((x) => [x.name, x.division, x.status, x.id]))); }
function renderTeams(data) { $("view").append(table(["Team", "Description", "Tasks", "ID"], data.map((x) => [x.name, x.description, (x.tasks || []).length, x.id]))); }
function renderWorkflows(data) { $("view").append(table(["Workflow", "Purpose", "Steps", "ID"], data.map((x) => [x.name, x.purpose, (x.steps || []).length, x.id]))); }
function renderSkills(data) { $("view").append(table(["Skill", "Path"], data.map((x) => [x.id, x.path]))); }
function renderRuns(data) { $("view").append(table(["Run", "Action", "Status", "Subject"], data.map((x) => [x.id, x.action, x.status, x.subject]))); }
function renderOrganization(data) {
  const grid = el("div", undefined, "metric-grid"); grid.append(card("Teams", (data.teams || []).length, "organization teams"), card("Divisions", (data.division_assignments || []).length, "single-home assignments"), card("Workflows", (data.workflows || []).length, "evidence-gated definitions"));
  $("view").append(grid); $("view").append(table(["Team", "Lead", "Divisions", "Members"], (data.teams || []).map((x) => [x.name, x.lead_agent_id, (x.division_ids || []).length, (x.member_agent_ids || []).length])));
}
function renderGovernance(data) {
  const grid = el("div", undefined, "metric-grid"); grid.append(card("Permissions", (data.permissions || []).length, "declared permission rules"), card("Policies", (data.policies || []).length, "governance policies"), card("Capabilities", (data.capabilities || []).length, "known capabilities"));
  $("view").append(grid); $("view").append(table(["Capability", "Risk", "Description"], (data.capabilities || []).map((x) => [x.name, x.risk, x.description])));
}
function renderEvidence(data) {
  const grid = el("div", undefined, "metric-grid"); grid.append(card("Events", (data.events || []).length, "accepted control-plane events"), card("Runs", data.run_count || 0, "control records"), card("Queued", data.queued_runs || 0, "not executed by this surface"));
  $("view").append(grid); $("view").append(el("p", data.note || "", "muted")); if ((data.events || []).length) $("view").append(table(["Event", "Type", "Subject"], data.events.map((x) => [x.id, x.type, x.subject])));
}
function renderMemory(data) { const entries = data.entries || []; $("view").append(card("Entries", entries.length, data.note || "read-only")); if (entries.length) $("view").append(table(["ID", "Scope", "Status"], entries.map((x) => [x.id || "—", x.scope || "—", x.status || "—"]))); }
function renderEnvironments(data) { const c = data.current || {}; $("view").append(table(["Field", "Value"], [["Kind", c.kind], ["Platform", c.platform], ["Architecture", c.architecture], ["Python", c.python_version], ["Workspace", c.cwd], ["Mutations", data.mutations]])); }
function renderHarnesses(data) { $("view").append(table(["Adapter", "Path", "State"], data.map((x) => [x.id, x.path, x.state]))); }
function renderSettings(data) { const rows = [["API version", data.api_version], ["Default host", data.web?.default_host], ["Default port", data.web?.default_port], ["Remote", data.web?.remote], ["CORS", data.security?.cors], ["Telemetry", data.security?.telemetry], ["Mutation limit", data.security?.mutation_body_limit], ["Run creation", data.execution?.run_creation], ["Execution", data.execution?.execution]]; $("view").append(table(["Setting", "Value"], rows)); }

function svgNode(tag, attrs = {}) { const node = document.createElementNS(SVG_NS, tag); Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value))); return node; }
function graphKinds(mode) {
  if (mode === "workflow") return new Set(["workflow", "step", "team", "agent"]);
  if (mode === "capability") return new Set(["agent", "skill", "capability", "permission"]);
  return new Set(["team", "division", "agent"]);
}
function buildGraphLayout(data, mode, query) {
  const allowed = graphKinds(mode); const nodes = data.nodes.filter((n) => allowed.has(n.kind) && (!query || n.label.toLowerCase().includes(query)));
  const visible = new Set(nodes.map((n) => n.id)); const edges = data.edges.filter((e) => visible.has(e.source) && visible.has(e.target));
  const byKind = new Map(); nodes.forEach((node) => { if (!byKind.has(node.kind)) byKind.set(node.kind, []); byKind.get(node.kind).push(node); });
  const kinds = [...byKind.keys()].sort(); const positions = new Map(); const width = 1500; const rowGap = 120;
  kinds.forEach((kind, row) => { const items = byKind.get(kind); const gap = width / (items.length + 1); items.forEach((node, index) => positions.set(node.id, { x: Math.round(gap * (index + 1)), y: 90 + row * rowGap })); });
  return { nodes, edges, positions, width, height: Math.max(420, 160 + (kinds.length - 1) * rowGap) };
}
function renderGraph(data) {
  const mode = state.graph.mode; const query = ($("graph-search")?.value || "").trim().toLowerCase(); const layout = buildGraphLayout(data, mode, query);
  const wrap = $("graph-canvas"); clear(wrap); const svg = svgNode("svg", { viewBox: `0 0 ${layout.width} ${layout.height}`, role: "img", "aria-label": `${mode} relationship graph` });
  const viewport = svgNode("g", { transform: `translate(${state.graph.x} ${state.graph.y}) scale(${state.graph.scale})` }); const edges = svgNode("g", { class: "graph-edges" });
  layout.edges.forEach((edge) => { const a = layout.positions.get(edge.source); const b = layout.positions.get(edge.target); if (!a || !b) return; const line = svgNode("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y, class: `edge edge-${edge.relation.replaceAll(":", "-")}` }); line.dataset.relation = edge.relation; edges.append(line); }); viewport.append(edges);
  const nodes = svgNode("g", { class: "graph-nodes" });
  layout.nodes.forEach((node) => { const p = layout.positions.get(node.id); const group = svgNode("g", { class: `graph-node kind-${node.kind}`, transform: `translate(${p.x} ${p.y})`, tabindex: "0", role: "button", "aria-label": `${node.kind}: ${node.label}` }); const circle = svgNode("circle", { r: node.kind === "agent" ? 13 : 17 }); const label = svgNode("text", { x: 0, y: 32, "text-anchor": "middle" }); label.textContent = node.label.length > 26 ? `${node.label.slice(0, 24)}…` : node.label; group.append(circle, label); group.addEventListener("click", () => showNodeDetail(node, data)); group.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); showNodeDetail(node, data); } }); nodes.append(group); }); viewport.append(nodes); svg.append(viewport); wrap.append(svg); bindGraphPan(svg, viewport, layout); $("graph-count").textContent = `${layout.nodes.length} nodes · ${layout.edges.length} relationships`;
}
function showNodeDetail(node, data) {
  const panel = $("graph-detail"); clear(panel); panel.append(el("h3", node.label)); panel.append(el("p", `${node.kind} · ${node.id}`, "muted"));
  const details = Object.entries(node).filter(([key]) => !["id", "kind", "label"].includes(key));
  details.forEach(([key, value]) => panel.append(el("p", `${key}: ${Array.isArray(value) ? value.join(", ") || "—" : String(value)}`)));
  if (node.kind === "agent") {
    const related = data.edges.filter((edge) => edge.source === node.id || edge.target === node.id).length; panel.append(el("p", `Relationships: ${related}`));
  }
}
function bindGraphPan(svg, viewport, layout) {
  svg.addEventListener("wheel", (event) => { event.preventDefault(); const factor = event.deltaY < 0 ? 1.1 : 0.9; state.graph.scale = Math.min(2.8, Math.max(0.35, state.graph.scale * factor)); viewport.setAttribute("transform", `translate(${state.graph.x} ${state.graph.y}) scale(${state.graph.scale})`); }, { passive: false });
  svg.addEventListener("pointerdown", (event) => { if (event.target.closest(".graph-node")) return; state.graph.drag = { x: event.clientX, y: event.clientY, ox: state.graph.x, oy: state.graph.y }; svg.setPointerCapture(event.pointerId); });
  svg.addEventListener("pointermove", (event) => { if (!state.graph.drag) return; state.graph.x = state.graph.drag.ox + event.clientX - state.graph.drag.x; state.graph.y = state.graph.drag.oy + event.clientY - state.graph.drag.y; viewport.setAttribute("transform", `translate(${state.graph.x} ${state.graph.y}) scale(${state.graph.scale})`); });
  svg.addEventListener("pointerup", () => { state.graph.drag = null; });
  svg.addEventListener("pointercancel", () => { state.graph.drag = null; });
  $("graph-reset").onclick = () => { state.graph.scale = 1; state.graph.x = 0; state.graph.y = 0; renderGraph(dataForGraph()); };
}
function dataForGraph() { return state.cache.visualization || { nodes: [], edges: [], runs: [] }; }
function renderVisualization(data) {
  const controls = el("div", undefined, "graph-toolbar"); const modes = [["organization", "Organization"], ["workflow", "Workflows"], ["capability", "Skills & Security"]];
  modes.forEach(([id, label]) => { const button = el("button", label, `button graph-mode${state.graph.mode === id ? " active" : ""}`); button.type = "button"; button.dataset.mode = id; button.addEventListener("click", () => { state.graph.mode = id; renderVisualization(data); }); controls.append(button); });
  const search = el("input", undefined, "graph-search"); search.id = "graph-search"; search.type = "search"; search.placeholder = "Filter visible nodes"; search.setAttribute("aria-label", "Filter visible nodes"); search.value = $("graph-search")?.value || ""; search.addEventListener("input", () => renderGraph(data)); controls.append(search);
  const reset = el("button", "Reset view", "button"); reset.type = "button"; reset.id = "graph-reset"; controls.append(reset); $("view").append(controls);
  const shell = el("section", undefined, "graph-shell"); const canvas = el("div", undefined, "graph-canvas"); canvas.id = "graph-canvas"; shell.append(canvas); const detail = el("aside", undefined, "card graph-detail"); detail.id = "graph-detail"; detail.append(el("h3", "Select a node"), el("p", "Click a node to inspect its declared relationships and metadata.", "muted")); shell.append(detail); $("view").append(shell);
  const runPanel = el("article", undefined, "card"); const runs = data.runs || []; runPanel.append(el("h2", "Current execution state"), el("p", data.state_note || "", "muted"));
  runPanel.append(table(["Run", "Action", "Status", "Subject"], runs.map((x) => [x.id, x.action, x.status, x.subject]))); $("view").append(runPanel);
  renderGraph(data);
}

async function render(view) {
  const active = NAV.some(([id]) => id === view) ? view : "overview"; renderNav(active); $("page-title").textContent = NAV.find(([id]) => id === active)[1]; $("page-subtitle").textContent = DESCRIPTIONS[active];
  clear($("view")); $("error").hidden = true; state.loading = true;
  try {
    let data = state.cache[active]; if (!data) { data = await get(ENDPOINTS[active]); state.cache[active] = data; } setConnection(true);
    if (active === "overview") renderOverview(data); else if (active === "agents") renderAgents(data); else if (active === "teams") renderTeams(data); else if (active === "workflows") renderWorkflows(data);
    else if (active === "visualization") renderVisualization(data); else if (active === "skills") renderSkills(data); else if (active === "runs") renderRuns(data); else if (active === "organization") renderOrganization(data);
    else if (active === "governance") renderGovernance(data); else if (active === "evidence") renderEvidence(data); else if (active === "memory" || active === "knowledge") renderMemory(data); else if (active === "environments") renderEnvironments(data); else if (active === "harnesses") renderHarnesses(data); else if (active === "settings") renderSettings(data);
    $("updated").textContent = new Date().toLocaleTimeString();
  } catch (_error) { setConnection(false); $("error").hidden = false; $("error").textContent = "The Control Center could not read the requested live state."; $("view").append(el("p", "Check that the SI Web server is running and that the request is authorized.", "muted")); }
  finally { state.loading = false; }
}
$("refresh").addEventListener("click", () => { state.cache = {}; render(location.hash.slice(1) || "overview"); });
window.addEventListener("popstate", () => render(location.hash.slice(1) || "overview")); window.addEventListener("hashchange", () => render(location.hash.slice(1) || "overview"));
render(location.hash.slice(1) || "overview");
