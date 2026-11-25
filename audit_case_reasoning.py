"""Audit approved case-reasoning additions without treating source matches as proof of inference."""
from pathlib import Path
from collections import defaultdict
import json,re,statistics
R=Path(__file__).resolve().parent;D=R/'content/命例拆解'
load=lambda p:json.loads(p.read_text())
norm=lambda s:re.sub(r'\s+','',s)
rows=load(D/'目录.json');approved=load(D/'批次.json');total=approved['approvedTotal']
assert total==936 and len(rows)==total
assert [r['order'] for r in rows]==list(range(1,total+1))
ids=[i for b in approved['batches'] for i in b['caseIds']]
assert len(ids)==len(set(ids))==total and set(ids)=={r['caseId'] for r in rows}
assert [b['count'] for b in approved['batches']]==[5,100,20,100,100,100,50,5,100,200,156]
assert len({r['file'] for r in rows})==total
assert {r['file'] for r in rows}=={p.name for p in D.glob('*.md')}
quiz_text=(R/'data/data-quiz.js').read_text()
quiz=json.loads(quiz_text.split('=',1)[1].strip().removesuffix(';'))
by_id={q['id']:q for q in quiz['items']}
source_cache={};paragraphs=defaultdict(list);lengths=[];quote_count=0;flags=[]
for r in rows:
 p=D/r['file'];text=p.read_text();lengths.append(len(text))
 assert len(text)>900 and 'AI推理拆解' in text and '推断' in text,r['file']
 assert text.startswith('# ') and text.count('\n## ')>=3,r['file']
 if r['order']>5:
  chart=by_id[r['caseId']]['chart'];pairs=[''.join(p) for p in zip(chart['gan'],chart['zhi'])]
  top=text[:650];table=re.search(r'\| [乾坤]造 \| (.*?) \|\n',top)
  if table:assert [z.strip() for z in table[1].split('|')]==pairs,r['file']
  else:assert '、'.join(pairs) in top,r['file']
 assert not re.search(r'视频|奇门|六爻|段建业|卜文|言明|毛泽东|蒋介石|徐向前|周恩来|奥纳西斯|奥那西斯|薄一波|李嘉诚|夏仲奇|赵宇',text),r['file']
 assert len(r['evidence'])>=2 and len({(e['file'],norm(e['quote'])) for e in r['evidence']})==len(r['evidence']),r['file']
 for e in r['evidence']:
  src=(R/e['file']).resolve();assert src.is_relative_to((R/'content').resolve()) or src.is_relative_to((R/'_src/txt').resolve()),e
  if src not in source_cache:source_cache[src]=norm(src.read_text())
  assert len(norm(e['quote']))>=6 and norm(e['quote']) in source_cache[src],(r['file'],e)
  assert not re.search(r'视频|奇门|六爻|段建业|卜文|言明|毛泽东|蒋介石|徐向前|周恩来|奥纳西斯|奥那西斯|薄一波|李嘉诚|夏仲奇|赵宇',e['quote']),r['file']
  quote_count+=1
 core=re.split(r'\n## (?:对照依据|对照短据|出处|依据)',text)[0]
 for line in core.split('\n'):
  if len(line)>=65 and not line.startswith(('#','>','-','|')):paragraphs[norm(line)].append(r['order'])
 # Signals only: a risky word is not necessarily a wrong claim (e.g. a rebuttal).
 risky=re.findall(r'.{0,28}(?:必然|必定|一定会|永远|绝对|只要.{0,15}就).{0,42}',core)
 if risky:flags.append({'order':r['order'],'file':r['file'],'signals':risky})
repeats=[{'orders':v,'paragraph':k[:180]} for k,v in paragraphs.items() if len(v)>=3]
assert not repeats,('长段落模板重复',repeats)
print(f'通过：{total}例（5+100+20+100+100+100+50+5+100+200+156）、稳定ID/顺序、{quote_count}处可核短据、禁词、正文长度、无三篇共享长模板。')
print('篇长：',min(lengths),'—',max(lengths),'；中位数',statistics.median(lengths))
print('需要语义复核的强断词条目：',len(flags),'（信号不等于错误）')
if (R/'_src/reasoning_936').exists():
 (R/'_src/reasoning_936/audit-signals.json').write_text(json.dumps(flags,ensure_ascii=False,indent=2)+'\n')
