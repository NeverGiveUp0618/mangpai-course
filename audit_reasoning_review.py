"""Full-corpus provenance, reading-map and reviewed-regression checks."""
from pathlib import Path
import hashlib,json,re
from reasoning_maps import render_reasoning_map
R=Path(__file__).resolve().parent;D=R/'content/命例拆解'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=load(D/'目录.json');maps=load(D/'结构图.json');report=load(R/'reviews/reasoning-review-maps-20261125.json')
assert len(rows)==len(maps)==len(report['cases'])==936
cases={x['caseId']:x for x in report['cases']}
for r,m in zip(rows,maps):
 p=D/r['file'];text=p.read_text();assert sha(p)==cases[r['caseId']]['sha256'],r['order']
 rendered=render_reasoning_map(m,r,text)
 assert 'reasoning-map' in rendered and 'crm-node' in rendered
 if m['basis']=='paragraph-excerpts':
  headings=[re.sub(r'[*`>#]','',x).strip() for x in re.findall(r'^## (.*)$',text,re.M)]
  assert all(n['heading'] in headings for n in m['nodes']),r['order']
for c in report['changes']:
 assert sha(D/c['file'])==c['afterSha256']
 assert rows[c['order']-1]==c['updatedRow']
# These prevent real errors found in the review from silently coming back.
checks={375:('时丙食神','时丙伤官'),481:('寅申隔位相冲','寅木贴身冲申'),490:('日支未根','年支未根'),520:('癸水食神透干','癸水伤官透干'),720:('丙火正官、戊土正印','丙火正官、戊土偏印'),804:('癸水偏印','癸水正印'),808:('庚金正财透出','庚金偏财透出'),857:('庚金七杀生子印','庚金正印生扶'),926:('癸水食神透干','癸水偏财透干')}
for order,(good,bad) in checks.items():
 t=(D/rows[order-1]['file']).read_text();assert good in t and bad not in t,(order,good,bad)
assert '原盘并无亥' in (D/rows[839]['file']).read_text()
assert '现撤回' in (D/rows[846]['file']).read_text()
assert '不能恢复成已证实的完整推理' in (D/rows[874]['file']).read_text()
assert sum(m['basis']=='authored-reading-map' for m in maps)==25
print(f'通过：936正文版本与结构图溯源、25专写图/911折叠阅读结构、{len(report["changes"])}例订正记录及关键错误回归。')
