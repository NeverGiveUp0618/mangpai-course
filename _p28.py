import re, io
# ---------------- build_mp.py：课程正文按级别拆包 ----------------
p = 'build_mp.py'
b = open(p).read()
if 'data-body-' not in b:
    old = "    raw = {c['id']: {'html': c['html'], 'text': c['text']} for c in courses if c['raw']}\n    for c in courses:\n        if c['raw']:\n            c['html'] = ''\n            c['text'] = ''\n"
    new = """    raw = {c['id']: {'html': c['html'], 'text': c['text']} for c in courses if c['raw']}
    LVK = {'初级': 'chu', '中级': 'zhong', '高级': 'gao', '专题': 'zhuan'}
    bodies = {k: {} for k in LVK.values()}
    for c in courses:
        if c['raw']:
            c['html'] = ''
            c['text'] = ''
        else:
            bodies[LVK[c['level']]][c['id']] = {'html': c['html'], 'text': c['text']}
            c['html'] = ''
            c['text'] = ''
"""
    assert old in b
    b = b.replace(old, new, 1)
    b = b.replace("        ('data-raw.js', write_js('data-raw.js', 'DATA_RAW', raw)),", "        ('data-raw.js', write_js('data-raw.js', 'DATA_RAW', raw)),\n    ] + [('data-body-%s.js' % k, write_js('data-body-%s.js' % k, 'DATA_BODY_%s' % k, v)) for k, v in bodies.items()] + [", 1)
    open(p, 'w').write(b)

# ---------------- _patch_app.py：按需加载级别正文 ----------------
p = '_patch_app.py'
s = open(p).read()
if 'needBodyOf' not in s:
    marker = "io.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html"
    add = r'''# ---- 课程正文按级别拆包：先显示列表（秒开），点章节才拉该级别正文 ----
old = "var needRaw = function () { return need('data-raw.js', 'DATA_RAW'); };"
new = """var needRaw = function () { return need('data-raw.js', 'DATA_RAW'); };
var LVKEY = { '初级': 'chu', '中级': 'zhong', '高级': 'gao', '专题': 'zhuan' };
function needBodyOf(c) { return c.raw ? needRaw() : need('data-body-' + LVKEY[c.level] + '.js', 'DATA_BODY_' + LVKEY[c.level]); }
function needAllBodies(withRaw) {
  var ps = Object.keys(LVKEY).map(function (k) { return need('data-body-' + LVKEY[k] + '.js', 'DATA_BODY_' + LVKEY[k]); });
  if (withRaw) ps.push(needRaw());
  return Promise.all(ps).then(function (rs) { var m = {}; rs.forEach(function (R) { for (var k in R) m[k] = R[k]; }); return m; });
}"""
assert old in s
s = s.replace(old, new, 1)
# 章节渲染：无正文则按级别加载
old = "    if (c.raw && !c.html) {\n      $('#chapterBody').innerHTML = '<div class=\"empty\">载入原稿…</div>';\n      needRaw().then(function (R) { fillRaw(list, R); RENDER.chapter(n); });\n      return;\n    }"
new = "    if (!c.html) {\n      $('#chapterBody').innerHTML = '<div class=\"empty\">载入中…</div>';\n      needBodyOf(c).then(function (R) { fillRaw(list, R); RENDER.chapter(n); });\n      return;\n    }"
assert old in s
s = s.replace(old, new, 1)
# 搜索：需要全部正文
old = "Promise.all([needCourse(), needNotes(), needQuiz(), searchRaw ? needRaw() : Promise.resolve(null)]).then(function (r) {\n    if (r[3]) fillRaw(r[0], r[3]);"
new = "Promise.all([needCourse(), needNotes(), needQuiz(), needAllBodies(searchRaw)]).then(function (r) {\n    if (r[3]) fillRaw(r[0], r[3]);"
assert old in s
s = s.replace(old, new, 1)
s = s.replace("  box.innerHTML = '<div class=\"empty\">搜索中…</div>';", "  box.innerHTML = '<div class=\"empty\">搜索中…（首次搜索要加载全部教材，稍候）</div>';", 1)
'''
    s = s.replace(marker, add + marker, 1)
    open(p, 'w').write(s)

# ---------------- smoke：载入全部正文包 ----------------
p = 'smoke_mp.js'
t = open(p).read()
if 'data-body-chu' not in t:
    t = t.replace("'data/data-raw.js'].forEach(run);", "'data/data-raw.js', 'data/data-body-chu.js', 'data/data-body-zhong.js', 'data/data-body-gao.js', 'data/data-body-zhuan.js'].forEach(run);", 1)
    open(p, 'w').write(t)
print('ok')
