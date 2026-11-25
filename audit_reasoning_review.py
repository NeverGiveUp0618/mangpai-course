"""Full-corpus provenance, reading-map and reviewed-regression checks."""
from pathlib import Path
import hashlib,json,re
from reasoning_maps import render_reasoning_map
R=Path(__file__).resolve().parent;D=R/'content/命例拆解'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=load(D/'目录.json');maps=load(D/'结构图.json');report=load(R/'reviews/reasoning-review-maps-20261125.json')
assert len(rows)==len(report['cases'])==936
assert len(maps)==25 and len({m['caseId'] for m in maps})==25
style=load(R/'reviews/reasoning-style-20261125.json')
rewrites={c['file']:c for c in style['changes']}
assert len(rewrites)==25 and style['removedParagraphMaps']==911
cases={x['caseId']:x for x in report['cases']}
for r in rows:
 p=D/r['file'];expected=cases[r['caseId']]['sha256']
 if r['file'] in rewrites:
  c=rewrites[r['file']];assert c['beforeSha256']==expected
  expected=c['afterSha256']
 assert sha(p)==expected,r['order']
by_id={r['caseId']:r for r in rows}
for m in maps:
 r=by_id[m['caseId']];text=(D/r['file']).read_text()
 assert m['basis']=='authored-reading-map'
 assert text.count('<div data-reasoning-map-slot></div>')==1
 rendered=render_reasoning_map(m,r,text)
 assert 'reasoning-map' in rendered and '<pre><code>' in rendered
for c in report['changes']:
 assert rewrites.get(c['file'],{}).get('beforeSha256',sha(D/c['file']))==c['afterSha256']
 assert rows[c['order']-1]==c['updatedRow']
# These prevent real errors found in the review from silently coming back.
checks={375:('时丙食神','时丙伤官'),481:('隔位相冲','寅木贴身冲申'),490:('日支未根','年支未根'),520:('癸水食神透干','癸水伤官透干'),720:('丙火正官、戊土正印','丙火正官、戊土偏印'),804:('癸水偏印','癸水正印'),808:('庚金正财透出','庚金偏财透出'),857:('庚金七杀生子印','庚金正印生扶'),926:('癸是食神','癸水偏财透干')}
for order,(good,bad) in checks.items():
 t=(D/rows[order-1]['file']).read_text();assert good in t and bad not in t,(order,good,bad)
assert '原盘并无亥' in (D/rows[839]['file']).read_text()
assert '现撤回' in (D/rows[846]['file']).read_text()
assert '不能恢复成已证实的完整推理' in (D/rows[874]['file']).read_text()
assert sum(m['basis']=='authored-reading-map' for m in maps)==25

for order in (889,926):
 t=(D/rows[order-1]['file']).read_text();assert '站内题盘四柱' in t and '撤回' in t and '文字版' in t
assert '盘源对照' in (D/rows[925]['file']).read_text()
print(f'通过：936正文版本与结构图溯源、25篇正文重写/专写图、911折叠提纲已移除、{len(report["changes"])}例订正记录及关键错误回归。')

flows=load(R/'reviews/reasoning-flow-20261125.json')
assert flows['scope']==25
for m,c in zip(maps,flows['cases']):
 assert m['caseId']==c['caseId'] and hashlib.sha256(m['flow'].encode()).hexdigest()==c['flowSha256']
 assert 'nodes' not in m
