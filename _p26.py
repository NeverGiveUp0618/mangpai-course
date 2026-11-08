import os, re, io, shutil
base = 'content/教材'
os.makedirs(os.path.join(base, '专题'), exist_ok=True)
src = os.path.join(base, '中级')
moved = []
for fn in sorted(os.listdir(src)):
    m = re.match(r'^(\d+)-(.+)\.md$', fn)
    if m and 18 <= int(m.group(1)) <= 28:
        moved.append(fn)
for k, fn in enumerate(moved, 1):
    rest = re.sub(r'^\d+-', '', fn)
    shutil.move(os.path.join(src, fn), os.path.join(base, '专题', '%02d-%s' % (k, rest)))
print('移动', len(moved))

# 专题章节按主题顺序编号（原编号 18..28 顺序不一，按标题重排）
d = os.path.join(base, '专题')
order = ['体用与宾主作用专题', '应期与墓穿专题', '伤官、六亲与命格组合专题', '象法与象的应用专题', '职业专题（一）', '职业专题（二）', '疾病专题', '婚姻问答专题',
         '答疑汇编专题（一）', '答疑汇编专题（二）', '命术轶闻断例精讲']
files = os.listdir(d)
tmp = []
for fn in files:
    t = io.open(os.path.join(d, fn), encoding='utf-8').read().split('\n', 1)[0].lstrip('# ').strip()
    idx = next((i for i, o in enumerate(order) if t.startswith(o)), 99)
    tmp.append((idx, t, fn))
tmp.sort()
for i, (idx, t, fn) in enumerate(tmp, 1):
    new = '%02d-%s.md' % (i, re.sub(r'[\\/:*?"<>|]', '', t)[:36])
    os.rename(os.path.join(d, fn), os.path.join(d, new + '.tmp'))
for fn in os.listdir(d):
    if fn.endswith('.tmp'):
        os.rename(os.path.join(d, fn), os.path.join(d, fn[:-4]))

# build_mp：加第四级「专题」
p = 'build_mp.py'
b = open(p).read()
b = b.replace("LEVELS = ['初级', '中级', '高级']", "LEVELS = ['初级', '中级', '高级', '专题']", 1)
# THEMES 里的专题章节改成 level='专题'：find() 按级别取，三列之外加一列太宽 → 主题表后另列「专题」
b = b.replace("'体用与宾主作用专题'], ['体用宾主']),", "], ['体用宾主']),").replace(", '象法与象的应用专题', '伤官、六亲与命格组合专题'],", "],").replace("['应期与墓穿专题'],", "[],").replace("['象的应用', '答疑汇编专题'],", "['象的应用'],").replace("['婚姻专辑', '婚姻问答专题'],", "['婚姻专辑'],").replace("['学历与牢狱', '实战演示', '命术轶闻'],", "['学历与牢狱', '实战演示'],").replace("('疾病', [], ['疾病专题'], []),\n", "").replace("['职业专题'], ['职业象法']", "[], ['职业象法']")
open(p, 'w').write(b)
print('build_mp 已调整')
