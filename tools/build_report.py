from pathlib import Path
import html, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from engiproof import __version__
from engiproof.core import list_studies, verify_study
rows=[]
for m in list_studies():
    rows.append((m,verify_study(m['paper_id'])))
body=[]
for m,v in rows:
    tools='<br>'.join(html.escape(t['name']) for t in m.get('tools',[]))
    body.append(f"<tr><td>{m['paper_id']}</td><td>{html.escape(m['title'])}</td><td>{m['evidence_status']}</td><td>{v['status']}</td><td>{html.escape(str(v.get('qualification','NOT_CLAIMED')))}</td><td>{tools}</td></tr>")
doc=(f'<!doctype html><html><head><meta charset="utf-8"><title>EngiProof {__version__}</title>'
     '<style>body{font-family:Arial,sans-serif;max-width:1180px;margin:40px auto;padding:0 18px;line-height:1.45}table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbb;padding:8px;vertical-align:top}code,pre{background:#f3f3f3;padding:2px 4px}.note{border-left:4px solid #555;padding:10px 14px;background:#f7f7f7}</style></head><body>'
     f'<h1>EngiProof {__version__}</h1><p><strong>From Published Research to Verified Engineering.</strong></p>'
     '<div class="note">Runnable evidence is not the same as engineering qualification. Evidence status and qualification remain separate.</div>'
     '<h2>Live studies</h2><table><tr><th>ID</th><th>Paper</th><th>Evidence status</th><th>Verification</th><th>Qualification</th><th>Callable tools</th></tr>'
     + ''.join(body) +
     '</table><h2>Run</h2><pre>engiproof doctor\nengiproof list\nengiproof verify-all\nengiproof evidence P38\nengiproof discrepancy P38</pre>'
     '<p>See README.md and docs/CONTRACTS_v0.1.1.md.</p></body></html>')
(ROOT/'reports'/'index.html').write_text(doc,encoding='utf-8')
print('Built reports/index.html')
