const state = { data: {}, view: 'overview', refreshTimer: null };
const $ = (id) => document.getElementById(id);
const esc = (v) => String(v ?? '').replace(/[&<>\"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));

async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { Accept: 'application/json', ...(options.headers || {}) } });
  const text = await response.text();
  let body = {}; try { body = text ? JSON.parse(text) : {}; } catch (_) { body = { message: text }; }
  if (!response.ok) throw new Error(body.message || `HTTP ${response.status}`);
  return body;
}

async function load() {
  try {
    const [snapshot, health, agents, teams, workflows, events, runs, evidence, visualization, environments, settings] = await Promise.all([
      api('/api/v1'), api('/api/v1/health'), api('/api/v1/agents'), api('/api/v1/teams'), api('/api/v1/workflows'),
      api('/api/v1/events'), api('/api/v1/runs'), api('/api/v1/evidence'), api('/api/v1/visualization'), api('/api/v1/environments'), api('/api/v1/settings')
    ]);
    state.data = { snapshot, health, agents, teams, workflows, events, runs, evidence, visualization, environments, settings };
    $('health').textContent = 'Core healthy'; $('health').className = 'status ok'; render();
  } catch (error) {
    $('health').textContent = 'Degraded / disconnected'; $('health').className = 'status bad'; showError(error.message);
  }
}
function showError(message) { $('error').textContent = message; $('error').classList.remove('hidden'); setTimeout(() => $('error').classList.add('hidden'), 5000); }
function render() {
  const d = state.data, counts = d.snapshot?.counts || {};
  $('cards').innerHTML = Object.entries(counts).map(([k,v]) => `<article class="card"><span>${esc(k)}</span><strong>${esc(v)}</strong></article>`).join('');
  $('snapshot').textContent = JSON.stringify(d.snapshot, null, 2);
  $('events').innerHTML = (d.events || []).slice().reverse().map(e => `<article class="item"><strong>${esc(e.event_type)}</strong><span>${esc(e.subject)}</span><code>${esc(e.id)}</code><details><summary>metadata</summary><pre>${esc(JSON.stringify(e.metadata || {}, null, 2))}</pre></details></article>`).join('') || '<p class="muted">No events.</p>';
  $('workflowsList').innerHTML = (d.workflows || []).map(w => `<article class="item"><strong>${esc(w.name)}</strong><span>${esc(w.id)}</span><p>${esc(w.purpose)}</p><small>${(w.steps || []).length} steps</small></article>`).join('') || '<p class="muted">No workflows.</p>';
  $('runsList').innerHTML = (d.runs || []).map(r => `<article class="item"><strong>${esc(r.status)}</strong><span>${esc(r.id)}</span><code>${esc(r.subject || '')}</code><details><summary>run data</summary><pre>${esc(JSON.stringify(r, null, 2))}</pre></details></article>`).join('') || '<p class="muted">No runs.</p>';
  const nodes = d.visualization?.nodes || [], edges = d.visualization?.edges || [];
  $('topologyList').innerHTML = `<div class="graphmeta"><strong>${nodes.length}</strong> nodes · <strong>${edges.length}</strong> edges</div>` + nodes.map(n => `<article class="item"><strong>${esc(n.kind)}</strong> ${esc(n.label)} <code>${esc(n.id)}</code><p>${esc((edges.filter(e => e.source === n.id).map(e => `${e.relation} → ${e.target}`).join(' · ')) || 'No outgoing relations')}</p></article>`).join('');
  $('evidenceView').innerHTML = `<pre>${esc(JSON.stringify(d.evidence, null, 2))}</pre>`;
  $('resourcesView').innerHTML = Object.entries(d.environments?.current || {}).map(([k,v]) => `<article class="card"><span>${esc(k)}</span><strong>${esc(v)}</strong></article>`).join('');
  $('settingsView').innerHTML = `<pre>${esc(JSON.stringify(d.settings, null, 2))}</pre>`;
  renderApprovals();
}
async function renderApprovals() {
  try {
    const params = new URLSearchParams(); const subject = localStorage.getItem('si_subject'); const project = localStorage.getItem('si_project');
    if (subject) params.set('subject', subject); if (project) params.set('project', project);
    // The API requires identity headers; show a setup hint rather than guessing identity.
    if (!subject || !project) { $('approvalsList').innerHTML = '<p class="muted">Set <code>si_subject</code> and <code>si_project</code> in local storage to view identity-bound approvals.</p>'; return; }
    const approvals = await api('/api/v1/approvals', { headers: {'X-SI-Subject': subject, 'X-SI-Project': project} });
    $('approvalsList').innerHTML = approvals.map(a => `<article class="item"><strong>${esc(a.state)}</strong><span>${esc(a.gate)}</span><code>${esc(a.approval_id)}</code><p>${esc(a.reason || '')}</p></article>`).join('') || '<p class="muted">No pending approvals.</p>';
  } catch (error) { $('approvalsList').innerHTML = `<p class="muted">${esc(error.message)}</p>`; }
}
function switchView(view) { state.view = view; document.querySelectorAll('.view').forEach(x => x.classList.toggle('hidden', x.id !== view)); document.querySelectorAll('.nav button').forEach(x => x.classList.toggle('active', x.dataset.view === view)); document.querySelector(`#${view} h1`)?.focus?.(); }
document.querySelectorAll('.nav button').forEach(button => button.addEventListener('click', () => switchView(button.dataset.view)));
$('refresh').addEventListener('click', load);
$('eventSearch').addEventListener('input', (event) => { const q = event.target.value.toLowerCase(); document.querySelectorAll('#events .item').forEach(item => item.hidden = !item.textContent.toLowerCase().includes(q)); });
load(); state.refreshTimer = setInterval(load, 5000);
