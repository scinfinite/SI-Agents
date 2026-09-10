from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
for path in (ROOT/'agents').rglob('*.md'):
    if path.name=='README.md': continue
    lines=path.read_text(encoding='utf-8').splitlines()
    active=False
    for i,line in enumerate(lines):
        if line=='## Workflow': active=True; continue
        if active and line.startswith('## '): active=False
        if active and len(line)>2 and line[0].isdigit() and '. ' in line:
            prefix, value=line.split('. ',1)
            if prefix.isdigit(): lines[i]='- '+value
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=ROOT,check=True)
subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=ROOT,check=True)
subprocess.run(['git','add','agents'],cwd=ROOT,check=True)
subprocess.run(['git','commit','-m','fix(phase29): normalize workflow lists'],cwd=ROOT,check=True)
subprocess.run(['git','push'],cwd=ROOT,check=True)
