#!/usr/bin/env python3
"""一次性：把 bazi-course 的 app.js / index.html 改成盲派八字站。可重复运行（从 bazi-course 重新复制后再改）。"""
import re, io, os, shutil
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, '..', 'bazi-course')

for f in ('app.js', 'index.html', 'manifest.json'):
    shutil.copy(os.path.join(SRC, f), os.path.join(ROOT, f))

p = os.path.join(ROOT, 'app.js')
s = io.open(p, encoding='utf-8').read()

# 1) 去掉入站自检（那是小任八步法，本站没有）
a = s.index('(function initEntryGate() {')
b = s.index('\n})();', a) + len('\n})();')
s = s[:a] + s[b:]

# 2) 存储键换前缀，避免与同域的命理精讲串数据
s = s.replace('bazi_course_', 'mp_course_')
s = s.replace("counts: 'mp_course_counts',", "counts: 'mp_course_counts',\n  lvopen: 'mp_course_lvopen',")

# 3) 文案
s = s.replace('/* 命理精讲 — app.js', '/* 盲派八字 — app.js')
s = s.replace("home: '命理精讲', course: '教材 · 16章', chapter: '', notes: '笔记与索引',",
              "home: '盲派八字', course: '课程', chapter: '', notes: '专题与答疑',")
s = s.replace("TITLES[scr] || '命理精讲'", "TITLES[scr] || '盲派八字'")
s = s.replace("'<span class=\"pill g\">教材 ' + chDone", "'<span class=\"pill g\">课程 ' + chDone")
s = s.replace("'<span class=\"pill g\">笔记 ' + ntDone", "'<span class=\"pill g\">专题 ' + ntDone")
s = s.replace("[['chapter', '教材'], ['note', '笔记'], ['quiz', '命例']]", "[['chapter', '课程'], ['note', '专题'], ['quiz', '命例']]")
s = s.replace("if (l.scr === 'chapter') return '第 ' + l.id + ' 章';", "if (l.scr === 'chapter') return '课程 · 第 ' + l.id + ' 讲';")
s = s.replace("if (l.scr === 'note') return '笔记 ' + l.id;", "if (l.scr === 'note') return '专题 ' + l.id;")

# 4) 章页：去掉「去八字日练」卡
a = s.index("    // 看完一章去八字日练刷这一章的教材知识点")
b = s.index("    $('#prevCh').disabled")
s = s[:a] + "    var g = $('#chGame'); if (g) g.style.display = 'none';\n" + s[b:]

# 5) 课程列表：按 初/中/高 与册分组
a = s.index("RENDER.course = function () {")
b = s.index("/* 本章地图", a)
new_course = r"""RENDER.course = function () {
  var box = $('#courseList');
  box.innerHTML = '<div class="empty">载入中…</div>';
  needCourse().then(function (list) {
    var read = ls(K.read, {});
    var open = ls(K.lvopen, null);
    var last = ls(K.last, null);
    if (!open) {
      open = {};
      var cur = last && last.scr === 'chapter' ? list.filter(function (x) { return x.n === +last.id; })[0] : null;
      open[cur ? cur.level : '初级'] = 1;
    }
    function card(c) {
      var p = read[c.id] || 0;
      return '<div class="card tap" data-ch="' + c.n + '">' +
        '<div class="row spread"><div style="flex:1">' +
        '<b style="font-size:15.5px">' + esc(c.title) + '</b>' +
        '<div class="muted" style="margin-top:3px">' + Math.round(c.chars / 100) / 10 + ' 千字 · ' +
        c.toc.length + ' 节</div></div>' +
        (p >= 90 ? '<span class="pill">已读</span>' : p > 0 ?
          '<span class="pill g">' + p + '%</span>' : '<span style="color:var(--ink3)">›</span>') +
        '</div>' + (p > 0 && p < 90 ? '<div class="bar"><i style="width:' + p + '%"></i></div>' : '') +
        '</div>';
    }
    var html = '';
    (META.levels || []).forEach(function (L) {
      var lv = L.name;
      var tb = list.filter(function (x) { return x.level === lv && !x.raw; });
      var raw = list.filter(function (x) { return x.level === lv && x.raw; });
      var all = tb.concat(raw);
      if (!all.length) return;
      var dn = all.filter(function (x) { return (read[x.id] || 0) >= 90; }).length;
      var rawOpen = !!open[lv + '#raw'];
      html += '<div class="qgrp lvg' + (open[lv] ? ' open' : '') + '" data-g="' + esc(lv) + '">' +
        '<button class="qgh"><span class="ar">›</span><span class="nm">' + esc(lv) + '教材</span>' +
        '<span class="ct">' + dn + '/' + all.length + '</span></button><div class="qgb">' +
        (tb.length ? tb.map(card).join('') : '<div class="muted" style="padding:6px 14px">教材整理中</div>') +
        (raw.length ? '<div class="qgrp rawg' + (rawOpen ? ' open' : '') + '" data-g="' + esc(lv) + '#raw">' +
          '<button class="qgh"><span class="ar">›</span><span class="nm" style="font-weight:500;font-size:13px">原稿讲义（逐字整理，供查对）</span>' +
          '<span class="ct">' + raw.length + '</span></button><div class="qgb">' + raw.map(card).join('') + '</div></div>' : '') +
        '</div></div>';
    });
    box.innerHTML = html;
    $$('.qgh', box).forEach(function (b) {
      b.onclick = function (ev) {
        var g = b.parentNode, name = g.dataset.g;
        g.classList.toggle('open');
        var o = ls(K.lvopen, {}) || {};
        if (g.classList.contains('open')) o[name] = 1; else delete o[name];
        save(K.lvopen, o);
        ev.stopPropagation();
      };
    });
    $$('[data-ch]', box).forEach(function (el) {
      el.onclick = function () { show('chapter', +el.dataset.ch); };
    });
  });
};

"""
s = s[:a] + new_course + s[b:]
s = s.replace("$('#ttl').textContent = '第' + c.n + '章 · ' + c.title;", "$('#ttl').textContent = c.title;")
s = s.replace("/* 题库的可搜索全文。", "(function(){ var g = document.getElementById('gapCard'); if (g) g.onclick = function () { show('note', 1); }; })();\n\n/* 题库的可搜索全文。", 1)
# ---- 搜索：默认只搜教材与专题；原稿讲义按需加载 ----
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
# ---- 「我没学过」：掌握勾选 + 相关命例 ----
s = s.replace("  lvopen: 'mp_course_lvopen',", "  lvopen: 'mp_course_lvopen',\n  gap: 'mp_course_gap',", 1)
GAPTAGS = "['应期','应期','体用','桃花','墓库','墓库','穿','','体用','反局','体用','桃花']"
dec = """
var GAP_TAGS = %s;
function decorateGap() {
  var done = ls(K.gap, {});
  var hs = $$('#noteBody h3').filter(function (h) { return /^\\d+\\./.test(h.textContent.trim()); });
  hs.forEach(function (h, i) {
    var wrap = document.createElement('div');
    wrap.className = 'row wrap'; wrap.style.cssText = 'gap:8px;margin:2px 0 10px';
    var b = document.createElement('span'); b.className = 'pill ' + (done[i] ? '' : 'g'); b.style.cursor = 'pointer';
    b.textContent = done[i] ? '✓ 我已掌握' : '☐ 标记为已掌握';
    b.onclick = function () {
      var d = ls(K.gap, {}); if (d[i]) delete d[i]; else d[i] = 1; save(K.gap, d);
      b.className = 'pill ' + (d[i] ? '' : 'g'); b.textContent = d[i] ? '✓ 我已掌握' : '☐ 标记为已掌握';
    };
    wrap.appendChild(b);
    if (GAP_TAGS[i]) {
      var q = document.createElement('span'); q.className = 'pill g'; q.style.cursor = 'pointer';
      q.textContent = '相关命例（' + GAP_TAGS[i] + '）›';
      q.onclick = function () { qFilter.tag = GAP_TAGS[i]; qFilter.mode = 'all'; show('qlist', null); };
      wrap.appendChild(q);
    }
    h.parentNode.insertBefore(wrap, h.nextSibling);
  });
}
""" % GAPTAGS
s = s.replace("/* 题库的可搜索全文。", dec + "\n/* 题库的可搜索全文。", 1)
s = s.replace("    trackRead(c.id);\n    afterDoc($('#noteBody'), c.id);", "    trackRead(c.id);\n    afterDoc($('#noteBody'), c.id);\n    if (n === 1) decorateGap();", 1)
# 首页入口卡显示进度
s = s.replace("  var mn = myNotes().length;", "  var gd = Object.keys(ls(K.gap, {})).length, gh = $('#gapHint');\n  if (gh) gh.textContent = gd ? ('已掌握 ' + gd + ' 条 · 和你之前学的对照：哪些没讲过、在哪章读') : '和你之前学的对照：哪些没讲过、在哪章读、哪些口径不同';\n  var mn = myNotes().length;", 1)
s = s.replace("  $('#outlineBody').innerHTML = META.outline || '';\n  bindDoc($('#outlineBody'));", "  $('#outlineBody').innerHTML = META.outline || '';\n  bindDoc($('#outlineBody'));\n  $$('#outlineBody .chlink').forEach(function (a) { a.onclick = function () { show('chapter', +a.dataset.ch); }; });", 1)
# ---- 命例学习标记：不再自动记，改为用户手动打 ----
a = s.index("function markSeenLater(n) {")
b = s.index("function ls(k, d) {", a)
s = s[:a] + "function markSeenLater(n) { clearTimeout(seenTimer); /* 学习标记由用户在命例页手动打，不再自动记 */ }\n" + s[b:]
old = "    $('#L4').innerHTML =\n      '<div class=\"row spread\" id=\"qnav\""
new = "    var isSeen = !!ls(K.seen, {})[it.n];\n    $('#L4').innerHTML =\n      '<div class=\"row\" style=\"margin:18px 0 0\"><button class=\"btn' + (isSeen ? ' pri' : '') + '\" id=\"seenToggle\" style=\"flex:1\">' + (isSeen ? '✓ 已学（点一下取消）' : '☐ 标记为已学') + '</button></div>' +\n      '<div class=\"row spread\" id=\"qnav\""
assert old in s
s = s.replace(old, new, 1)
s = s.replace("    $('#bList').onclick = function () { show('qlist', null); };", "    $('#seenToggle').onclick = function () {\n      var sv = ls(K.seen, {}); if (sv[it.n]) delete sv[it.n]; else sv[it.n] = Date.now(); save(K.seen, sv);\n      var on = !!sv[it.n]; this.className = 'btn' + (on ? ' pri' : ''); this.textContent = on ? '✓ 已学（点一下取消）' : '☐ 标记为已学';\n    };\n    $('#bList').onclick = function () { show('qlist', null); };", 1)
s = s.replace("['new', '没看过'],", "['new', '未标记已学'],", 1)
# ---- 章节/专题阅读进度：不再滚动自动记，改为手动「标记为已读」 ----
old = "    var read = ls(K.read, {});\n    if (p > (read[id] || 0)) { read[id] = p; save(K.read, read); }\n    savePos(id);"
assert old in s
s = s.replace(old, "    savePos(id);   // 已读与否由用户手动标记，这里只记位置", 1)
fn = """
function addReadToggle(id, anchor) {
  var old = $('#readToggle'); if (old) old.parentNode.removeChild(old);
  var a = $(anchor); if (!a || !a.parentNode) return;
  var on = (ls(K.read, {})[id] || 0) >= 90;
  var b = document.createElement('button');
  b.id = 'readToggle'; b.className = 'btn' + (on ? ' pri' : ''); b.style.cssText = 'width:100%;margin:22px 0 0';
  b.textContent = on ? '✓ 已读（点一下取消）' : '☐ 标记为已读';
  b.onclick = function () {
    var r = ls(K.read, {}); if ((r[id] || 0) >= 90) delete r[id]; else r[id] = 100; save(K.read, r);
    var now = (r[id] || 0) >= 90; b.className = 'btn' + (now ? ' pri' : ''); b.textContent = now ? '✓ 已读（点一下取消）' : '☐ 标记为已读';
  };
  a.parentNode.parentNode.insertBefore(b, a.parentNode);
}
"""
s = s.replace("/* ---------- 题库 ---------- */", fn + "\n/* ---------- 题库 ---------- */", 1)
s = s.replace("    trackRead(c.id);\n    afterDoc($('#chapterBody'), c.id);", "    trackRead(c.id);\n    addReadToggle(c.id, '#prevCh');\n    afterDoc($('#chapterBody'), c.id);", 1)
s = s.replace("    trackRead(c.id);\n    afterDoc($('#noteBody'), c.id);", "    trackRead(c.id);\n    addReadToggle(c.id, '#prevNt');\n    afterDoc($('#noteBody'), c.id);", 1)
io.open(p, 'w', encoding='utf-8').write(s)

# ───── index.html ─────
p = os.path.join(ROOT, 'index.html')
h = io.open(p, encoding='utf-8').read()
a = h.index('<div class="entry-gate"'); b = h.index('\n</div>\n', a) + len('\n</div>\n')
h = h[:a] + h[b:]
h = h.replace('命理精讲', '盲派八字').replace('实用八字 · 系统教材与命例题库', '盲派命理 · 初中高级课程与命例库')
h = h.replace('实用八字系统教材、笔记与命例题库', '盲派八字初中高级课程、专题答疑与命例库')
h = h.replace('<span>章教材</span>', '<span>讲课程</span>').replace('<span>篇笔记</span>', '<span>篇专题</span>')
h = h.replace('<span>16章通读</span>', '<span>初·中·高</span>').replace('<span>笔记与索引</span>', '<span>专题与答疑</span>')
# 去掉不适用的首页卡：断命台 / v课笔记 / 问题清单 / 复习卡
for key in ('desk-entry', 'vke-entry'):
    m = re.search(r'\n    <div class="card tap %s".*?\n    </div>\n' % key, h, re.S)
    if m: h = h.replace(m.group(0), '\n')
for go in ('index', 'review'):
    m = re.search(r'\n    <div class="card tap" data-go="%s">.*?\n    </div>\n' % go, h, re.S)
    if m: h = h.replace(m.group(0), '\n')
h = h.replace('<script async src="https://nevergiveup0618.github.io/all-project/guard.js?reload=1"></script>',
              '<script async src="https://nevergiveup0618.github.io/all-project/guard.js?reload=1"></script>')
# 底栏：去掉「速」
h = re.sub(r'\s*<button data-tab="ref">.*?</button>', '', h)
h = h.replace('<span>教材</span>', '<span>课程</span>').replace('<span>笔记</span></button>', '<span>专题</span></button>')
h = h.replace('theme-color" content="#1f5673"', 'theme-color" content="#2d5a4b"')
io.open(p, 'w', encoding='utf-8').write(h)

h = h.replace('学习路线与依赖图','学习路线').replace('先学哪章、后学哪章','初 → 中 → 高，按什么顺序学')
io.open(p, 'w', encoding='utf-8').write(h)
h = h.replace('    <div class="card" id="progCard">', '''    <div class="card tap" id="gapCard">
      <div class="row spread">
        <div><b style="font-size:15px">🔎 我没学过 · 对照清单</b>
          <div class="muted" style="margin-top:2px" id="gapHint">和你之前学的对照：哪些没讲过、在哪章读、哪些口径不同</div></div>
        <span style="color:var(--ink3)">&rsaquo;</span>
      </div>
    </div>

    <div class="card" id="progCard">''',1)
io.open(p, 'w', encoding='utf-8').write(h)
# manifest
p = os.path.join(ROOT, 'manifest.json')
m = io.open(p, encoding='utf-8').read().replace('命理精讲', '盲派八字').replace('#1f5673', '#2d5a4b')
io.open(p, 'w', encoding='utf-8').write(m)
print('patched')
