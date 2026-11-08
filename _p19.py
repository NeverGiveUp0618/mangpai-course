import re, io, os
# 1) convert.py：存疑盘不输出盘行与警告
p = 'convert.py'
s = open(p).read()
old = """            md.append('')
            md.append(pan_md(sex, gan, zhi))
            if stt == 'bad':
                md.append('')
                md.append('> ⚠️ 此盘干支组合不合历法（疑识别或原稿笔误），待对照原件校对。')
            md.append('')"""
new = """            if stt != 'bad':          # 存疑盘（不合历法）不进站
                md.append('')
                md.append(pan_md(sex, gan, zhi))
                md.append('')"""
assert old in s
s = s.replace(old, new, 1)
open(p, 'w').write(s)
# 2) build_mp.py：存疑命例不入命例库
p = 'build_mp.py'
b = open(p).read()
if "c.get('bad')" in b and 'skip_bad' not in b:
    b = b.replace("        key = (c['sex'], gan, zhi)\n", "        if c.get('bad'):   # skip_bad：存疑盘不收\n            continue\n        key = (c['sex'], gan, zhi)\n", 1)
    open(p, 'w').write(b)
# 3) 教材里已标待校对的盘行删掉
n = 0
for lv in ('初级', '中级', '高级'):
    d = os.path.join('content', '教材', lv)
    for fn in os.listdir(d):
        if not fn.endswith('.md'):
            continue
        q = os.path.join(d, fn)
        t = io.open(q, encoding='utf-8').read()
        lines = t.split('\n')
        keep = [l for l in lines if not (l.startswith('**乾造**') or l.startswith('**坤造**')) or '待校对' not in l]
        if len(keep) != len(lines):
            n += len(lines) - len(keep)
            io.open(q, 'w', encoding='utf-8').write('\n'.join(keep))
print('教材删盘行', n)
