#!/usr/bin/env python3
"""教材 vs 原稿 抽查：①盘面干支是否在原稿出现 ②关键术语/作用方式条目有无丢失 ③大运行。报告写到 _src/verify_report.md。"""
import os, re, io, glob, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
C = os.path.join(ROOT, 'content')
GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
PAN = re.compile(r'\*\*(?:乾|坤)造\*\*[：:]\s*([%s]{4})[／/]([%s]{4})' % (GAN, ZHI))


def rd(p):
    return io.open(p, encoding='utf-8').read()


raw_all = {}
for lv in ('初级', '中级', '高级', '专题'):
    raw_all[lv] = '\n'.join(rd(p) for p in sorted(glob.glob('%s/%s/*.md' % (C, lv))))
raw_corpus = '\n'.join(raw_all.values())
# 原稿里的盘（含案例集解析出来的）
NORM = re.sub(r'[^\u4e00-\u9fff]', '', ''.join(rd(f) for f in glob.glob(os.path.join(ROOT, '_src', 'txt', '*.txt'))))
rawpans = set(m.group(1) + '/' + m.group(2) for m in PAN.finditer(raw_corpus))
import json
for c in json.load(io.open(os.path.join(ROOT, '_src', 'cases.json'), encoding='utf-8')):
    rawpans.add(c['gan'] + '/' + c['zhi'])

out = ['# 教材抽查报告\n']
tot = miss = 0
missing_pans = []
tb = {}
for lv in ('初级', '中级', '高级'):
    tb[lv] = '\n'.join(rd(p) for p in sorted(glob.glob('%s/教材/%s/*.md' % (C, lv))))
    for p in sorted(glob.glob('%s/教材/%s/*.md' % (C, lv))):
        for m in PAN.finditer(rd(p)):
            tot += 1
            k = m.group(1) + '/' + m.group(2)
            if k not in rawpans and (m.group(1) + m.group(2)) not in NORM:
                miss += 1
                missing_pans.append((lv, os.path.basename(p), k))
out.append('## 一、盘面\n教材里共 %d 个盘，其中 **%d 个在原稿里找不到同款干支**（可能是 OCR 校订、笔误订正，需人工看一眼）。\n' % (tot, miss))
for x in missing_pans:
    out.append('- %s · %s：%s' % x)

# 作用方式条目：干支对＋作用
OPS = '合|冲|穿|刑|破|害|暗合|半合|拱'
PAIR = re.compile(r'([%s])([%s])(合|冲|穿|刑|破|害|暗合|半合|拱)' % (ZHI, ZHI))
rawc = collections.Counter(m.group(0) for m in PAIR.finditer(raw_all['初级'] + raw_all['中级'] + raw_all['高级']))
tbc = collections.Counter(m.group(0) for m in PAIR.finditer(tb['初级'] + tb['中级'] + tb['高级']))
lost = [(k, n) for k, n in rawc.most_common() if n >= 6 and tbc.get(k, 0) == 0]
out.append('\n## 二、作用方式条目\n原稿里出现 ≥6 次、教材里却 0 次的「X Y 作用」：%d 条。\n' % len(lost))
for k, n in lost:
    out.append('- %s（原稿 %d 次）' % (k, n))

# 术语
TERMS = ['宾主', '体用', '功神', '废神', '虚透', '带象', '换象', '借象', '合象', '化象', '墓象', '共象', '禄', '原身', '连根', '包局', '反局', '正局', '正用', '反用',
         '贼神', '捕神', '合绊', '合留', '合动', '闭库', '开库', '入墓', '暗合', '三合局', '羊刃', '关财门', '官当财', '伤官当财', '禄当财', '桃花', '空亡', '伏吟',
         '遁藏', '透干', '大限', '交脱诀', '副宫', '穿倒', '穿偏', '冲起', '冲动', '冲开', '晦火', '死木', '活木', '干支一体', '化气', '气库', '形墓', '杀印相生',
         '伤官佩印', '羊刃架杀', '食伤泄秀', '比劫争夫', '能量', '效率', '驿马', '日主坐库', '财官临墓', '天地合', '拱合', '夹']
out.append('\n## 三、术语\n原稿出现 ≥5 次、教材 0 次：')
lostt = [(t, sum(raw_all[l].count(t) for l in ('初级', '中级', '高级'))) for t in TERMS]
lostt = [(t, n) for t, n in lostt if n >= 5 and sum(tb[l].count(t) for l in tb) == 0]
for t, n in lostt:
    out.append('- %s（原稿 %d 次）' % (t, n))
if not lostt:
    out.append('- 无')
out.append('\n教材各术语出现总次数（教材/原稿，越低越要留意）：')
rows = []
for t in TERMS:
    a = sum(tb[l].count(t) for l in tb)
    b = sum(raw_all[l].count(t) for l in ('初级', '中级', '高级'))
    if b >= 15:
        rows.append((a / b, t, a, b))
rows.sort()
for r, t, a, b in rows[:20]:
    out.append('- %s：%d / %d' % (t, a, b))
io.open(os.path.join(ROOT, '_src', 'verify_report.md'), 'w', encoding='utf-8').write('\n'.join(out))
print('盘', tot, '原稿无同款', miss, '| 丢失作用方式条目', len(lost), '| 丢失术语', len(lostt))
print('\n'.join(out[-24:]))
