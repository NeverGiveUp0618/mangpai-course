"""Full-corpus provenance, reading-map and reviewed-regression checks."""
from pathlib import Path
import hashlib,json,re
from reasoning_maps import render_reasoning_map
R=Path(__file__).resolve().parent;D=R/'content/命例拆解'
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=load(D/'目录.json');maps=load(D/'结构图.json');report=load(R/'reviews/reasoning-review-maps-20261125.json')
assert len(rows)==len(report['cases'])==936
assert len(maps)==936 and len({m['caseId'] for m in maps})==936
style=load(R/'reviews/reasoning-style-20261125.json')
style2=load(R/'reviews/reasoning-style-batch2-20261125.json')
style3=load(R/'reviews/reasoning-style-batch3-20261125.json')
style4=load(R/'reviews/reasoning-style-batch4-20261125.json')
style5=load(R/'reviews/reasoning-style-batch5-fix-20261126.json')
rewrites={c['file']:c for c in style['changes']}
rewrites2={c['file']:c for c in style2['changes']}
rewrites3={c['file']:c for c in style3['changes']}
rewrites4={c['file']:c for c in style4['changes']}
rewrites5={c['file']:c for c in style5['changes']}
assert len(rewrites)==25 and len(rewrites2)==100 and len(rewrites3)==700 and len(rewrites4)==111 and len(rewrites5)==3 and style['removedParagraphMaps']==911
cases={x['caseId']:x for x in report['cases']}
for r in rows:
 p=D/r['file'];expected=cases[r['caseId']]['sha256']
 if r['file'] in rewrites:
  c=rewrites[r['file']];assert c['beforeSha256']==expected
  expected=c['afterSha256']
 if r['file'] in rewrites2:
  c=rewrites2[r['file']];assert c['beforeSha256']==expected
  expected=c['afterSha256']
 if r['file'] in rewrites3:
  c=rewrites3[r['file']];assert c['beforeSha256']==expected
  expected=c['afterSha256']
 if r['file'] in rewrites4:
  c=rewrites4[r['file']];assert c['beforeSha256']==expected
  expected=c['afterSha256']
 if r['file'] in rewrites5:
  c=rewrites5[r['file']];assert c['beforeSha256']==expected
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
 cur_sha=rewrites.get(c['file'],{}).get('beforeSha256') or rewrites2.get(c['file'],{}).get('beforeSha256') or rewrites3.get(c['file'],{}).get('beforeSha256') or rewrites4.get(c['file'],{}).get('beforeSha256') or rewrites5.get(c['file'],{}).get('beforeSha256') or sha(D/c['file'])
 assert cur_sha==c['afterSha256']
 assert rows[c['order']-1]==c['updatedRow']
# These prevent real errors found in the review from silently coming back.
checks={375:('时丙食神','时丙伤官'),481:('隔位相冲','寅木贴身冲申'),490:('日支未根','年支未根'),520:('癸水食神透干','癸水伤官透干'),720:('丙火正官、戊土正印','丙火正官、戊土偏印'),804:('癸水偏印','癸水正印'),808:('庚金正财透出','庚金偏财透出'),857:('庚金七杀生子印','庚金正印生扶'),926:('癸是食神','癸水偏财透干')}
for order,(good,bad) in checks.items():
 t=(D/rows[order-1]['file']).read_text();assert good in t and bad not in t,(order,good,bad)
assert '原盘并无亥' in (D/rows[839]['file']).read_text()
assert '现撤回' in (D/rows[846]['file']).read_text()
assert '不能恢复成已证实的完整推理' in (D/rows[874]['file']).read_text()
assert sum(m['basis']=='authored-reading-map' for m in maps)==936

for order in (889,926):
 t=(D/rows[order-1]['file']).read_text();assert '站内题盘四柱' in t and '撤回' in t and '文字版' in t
assert '盘源对照' in (D/rows[925]['file']).read_text()
print(f'通过：936正文版本与结构图溯源、936篇正文重写/专写图、911折叠提纲已移除、{len(report["changes"])}例订正记录及关键错误回归。')

flows=load(R/'reviews/reasoning-flow-20261125.json')
assert flows['scope']==25
by_map={m['caseId']:m for m in maps}
for c in flows['cases']:
 m=by_map[c['caseId']]
 assert hashlib.sha256(m['flow'].encode()).hexdigest()==c['flowSha256']
 assert 'nodes' not in m
flows2=load(R/'reviews/reasoning-flow-batch2-20261125.json')
assert flows2['scope']==125
for c in flows2['cases']:
 m=by_map[c['caseId']]
 assert hashlib.sha256(m['flow'].encode()).hexdigest()==c['flowSha256']
 assert 'nodes' not in m
flows3=load(R/'reviews/reasoning-flow-batch3-20261125.json')
assert flows3['scope']==825
for c in flows3['cases']:
 m=by_map[c['caseId']]
 if m['order'] not in (241,786): assert hashlib.sha256(m['flow'].encode()).hexdigest()==c['flowSha256']
 assert 'nodes' not in m
flows4=load(R/'reviews/reasoning-flow-batch4-20261125.json')
assert flows4['scope']==936 and len(flows4['cases'])==936
flows5=load(R/'reviews/reasoning-flow-batch5-fix-20261126.json')
assert flows5['scope']==936
for m,c in zip(maps,flows5['cases']):
 assert m['caseId']==c['caseId'] and hashlib.sha256(m['flow'].encode()).hexdigest()==c['flowSha256']
 assert 'nodes' not in m
