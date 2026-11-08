p = '_patch_app.py'
s = open(p).read()
a = s.index('old = "    r[0].forEach(function (c) { scan(c.text')
b = s.index("io.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html")
new = r'''# ---- 搜索：默认只搜教材与专题；原稿讲义按需加载 ----
old = "    r[0].forEach(function (c) { scan(c.text, '第' + c.n + '章 · ' + c.title, 'chapter', c.n); });"
new = """    r[0].forEach(function (c) {
      if (c.raw && !searchRaw) return;
      scan(c.text, (c.raw ? '原稿 · ' : '') + c.title, 'chapter', c.n);
    });"""
assert old in s
s = s.replace(old, new, 1)
s = s.replace("function doSearch() {", "var searchRaw = false;\nfunction doSearch() {", 1)
s = s.replace("Promise.all([needCourse(), needNotes(), needQuiz()]).then(function (r) {",
              "Promise.all([needCourse(), needNotes(), needQuiz(), searchRaw ? needRaw() : Promise.resolve(null)]).then(function (r) {\n    if (r[3]) fillRaw(r[0], r[3]);", 1)
hint = """    var rawHint = !searchRaw ? '<div class="hit" id="rawHit"><b>也搜原稿讲义？</b><p>默认只搜教材与专题（原稿是逐字整理、与教材重叠）。点这里连原稿讲义一起搜（会多加载约 3MB）。</p></div>' : '';
    function bindRaw() { var e = $('#rawHit'); if (e) e.onclick = function () { searchRaw = true; doSearch(); }; }
"""
s = s.replace("    if (!hits.length) {\n      box.innerHTML = '<div class=\"empty\">没找到'", hint + "    if (!hits.length) {\n      box.innerHTML = '<div class=\"empty\">没找到'", 1)
s = s.replace("                     : '「' + esc(kw) + '」') + '</div>';\n      return;", "                     : '「' + esc(kw) + '」') + '</div>' + rawHint;\n      bindRaw();\n      return;", 1)
s = s.replace("          '<p>' + h.snip + '</p></div>';\n      }).join('');", "          '<p>' + h.snip + '</p></div>';\n      }).join('') + rawHint;\n    bindRaw();", 1)
s = s.replace('RENDER.search = function () {', 'RENDER.search = function () { searchRaw = false;', 1)
# ---- 原稿正文懒加载 ----
s = s.replace("var needCourse = function () { return need('data-course.js', 'DATA_COURSE'); };",
              "var needCourse = function () { return need('data-course.js', 'DATA_COURSE'); };\nvar needRaw = function () { return need('data-raw.js', 'DATA_RAW'); };\nfunction fillRaw(list, R) { list.forEach(function (c) { if (c.raw && !c.html && R[c.id]) { c.html = R[c.id].html; c.text = R[c.id].text; } }); }", 1)
old = "RENDER.chapter = function (n) {\n  needCourse().then(function (list) {\n    var c = list.filter(function (x) { return x.n === n; })[0];\n    if (!c) return;"
new = "RENDER.chapter = function (n) {\n  needCourse().then(function (list) {\n    var c = list.filter(function (x) { return x.n === n; })[0];\n    if (!c) return;\n    if (c.raw && !c.html) {\n      $('#chapterBody').innerHTML = '<div class=\"empty\">载入原稿…</div>';\n      needRaw().then(function (R) { fillRaw(list, R); RENDER.chapter(n); });\n      return;\n    }"
assert old in s
s = s.replace(old, new, 1)
'''
s = s[:a] + new + s[b:]
open(p, 'w').write(s)

# ---- build_mp：原稿正文拆到 data-raw.js ----
p = 'build_mp.py'
b = open(p).read()
if 'data-raw.js' not in b:
    b = b.replace("    sizes = [\n        ('data-course.js', write_js('data-course.js', 'DATA_COURSE', courses)),",
                  "    raw = {c['id']: {'html': c['html'], 'text': c['text']} for c in courses if c['raw']}\n    for c in courses:\n        if c['raw']:\n            c['html'] = ''\n            c['text'] = ''\n    sizes = [\n        ('data-raw.js', write_js('data-raw.js', 'DATA_RAW', raw)),\n        ('data-course.js', write_js('data-course.js', 'DATA_COURSE', courses)),")
    open(p, 'w').write(b)
# sw 预缓存不含 raw（按需），无需改
print('ok')
