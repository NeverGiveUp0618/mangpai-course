import os, re, io, sys
sys.path.insert(0, '.')
from proof import valid
base = 'content/教材'
PAN = re.compile(r'^(\*\*(?:乾|坤)造\*\*[：:]\s*([甲乙丙丁戊己庚辛壬癸]{4})[／/]([子丑寅卯辰巳午未申酉戌亥]{4}))(.*)$')
nfix = nbad = 0
for lv in ('初级', '中级', '高级'):
    d = os.path.join(base, lv)
    for fn in os.listdir(d):
        if not fn.endswith('.md'):
            continue
        p = os.path.join(d, fn)
        s = io.open(p, encoding='utf-8').read()
        o = s
        s = s.replace('夏仲奇', '本派前辈').replace('郝金阳', '本派前辈')
        out = []
        for l in s.split('\n'):
            m = PAN.match(l)
            if m and not valid(m.group(2), m.group(3)) and '待校对' not in l:
                l = l + '（原稿此盘待校对）'
                nbad += 1
            out.append(l)
        s = '\n'.join(out)
        if s != o:
            io.open(p, 'w', encoding='utf-8').write(s)
            nfix += 1
print('改动文件', nfix, '标待校对', nbad)

# build_mp：教材文件排序（一二三/上下 按语义序）
p = 'build_mp.py'
s = open(p).read()
if 'def tb_key' not in s:
    s = s.replace('def build_courses():', '''def tb_key(fn):
    m = re.match(r'^(\\d+)-(.*)$', fn)
    num = int(m.group(1)) if m else 0
    rest = m.group(2) if m else fn
    order = '上一二三四五六七八九十下'
    k = re.search(r'[（(]([上下一二三四五六七八九十])[）)]', rest)
    return (num, order.index(k.group(1)) if k else -1, rest)


def build_courses():''', 1)
    s = s.replace("            for fn in sorted(os.listdir(d)):\n                m = re.match(r'^(\\d+)-(.+)\\.md$', fn)\n                if m:\n                    add(os.path.join(d, fn), first_title(os.path.join(d, fn), m.group(2)), lv, '教材', False)",
                  "            for fn in sorted(os.listdir(d), key=tb_key):\n                m = re.match(r'^(\\d+)-(.+)\\.md$', fn)\n                if m:\n                    add(os.path.join(d, fn), first_title(os.path.join(d, fn), m.group(2)), lv, '教材', False)")
    open(p, 'w').write(s)
print('sorted key ok', 'tb_key' in s)
