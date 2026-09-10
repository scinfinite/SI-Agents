from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[1]
for path in (ROOT / 'agents').rglob('*.md'):
    if path.name == 'README.md':
        continue
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('# ') and line[2:] in {
            'Identity','Personality','Core Mission','Expertise','Responsibilities','Workflow',
            'Critical Rules','Boundaries','Deliverables','Failure Behavior','Escalation Behavior',
            'Verification Expectations','Evidence Requirements'}:
            lines[i] = '#' + line
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=ROOT,check=True)
subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=ROOT,check=True)
subprocess.run(['git','add','agents'],cwd=ROOT,check=True)
subprocess.run(['git','commit','-m','fix(phase29): normalize persona section headings'],cwd=ROOT,check=True)
subprocess.run(['git','push'],cwd=ROOT,check=True)
