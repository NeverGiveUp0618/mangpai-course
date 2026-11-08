#!/usr/bin/env python3
"""教材改写稿体检：盘面历法校验、禁用词、篇幅、结构。"""
import os, re, sys, io
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from proof import valid
BAN = ['视频', '六爻', '奇门', '梅花易', '段建业', '大任', '小任', '卜文', '郝金阳', '夏仲奇']
PAN = re.compile(r'\*\*(乾|坤)造\*\*[：:]\s*([甲乙丙丁戊己庚辛壬癸]{4})[／/]([子丑寅卯辰巳午未申酉戌亥]{4})')
base = os.path.join(ROOT, 'content', '教材')
tot = 0
bad_pan = []
issues = []
for lv in ('初级', '中级', '高级'):
    d = os.path.join(base, lv)
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.md'):
            continue
        s = io.open(os.path.join(d, fn), encoding='utf-8').read()
        tot += len(s)
        pans = PAN.findall(s)
        for sx, g, z in pans:
            if not valid(g, z):
                bad_pan.append((lv, fn, g + '/' + z))
        for w in BAN:
            if w in s:
                issues.append((lv, fn, '含「%s」×%d' % (w, s.count(w))))
        h2 = len(re.findall(r'^## ', s, re.M))
        print('%s %-34s %6d字 盘%2d ##%d%s' % (lv, fn[:32], len(s), len(pans), h2, '' if '<details>' in s else '  (无自测折叠)'))
print('总字数', tot)
print('盘面不合历法：', len(bad_pan))
for x in bad_pan:
    print('  ', x)
print('禁用词：', len(issues))
for x in issues:
    print('  ', x)
