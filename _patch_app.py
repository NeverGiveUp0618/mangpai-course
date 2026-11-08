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
    var html = '', lv = '', bk = '';
    list.forEach(function (c) {
      if (c.level !== lv) {
        lv = c.level; bk = '';
        var cnt = list.filter(function (x) { return x.level === lv; });
        var dn = cnt.filter(function (x) { return (read[x.id] || 0) >= 90; }).length;
        html += '<h3 class="lvh">' + esc(lv) + '<span class="muted"> · ' + dn + '/' + cnt.length + '</span></h3>';
      }
      if (c.book !== bk) { bk = c.book; html += '<div class="bkh">' + esc(bk) + '</div>'; }
      var p = read[c.id] || 0;
      html += '<div class="card tap" data-ch="' + c.n + '">' +
        '<div class="row spread"><div style="flex:1">' +
        '<b style="font-size:15.5px">' + esc(c.title) + '</b>' +
        '<div class="muted" style="margin-top:3px">' + Math.round(c.chars / 100) / 10 + ' 千字 · ' +
        c.toc.length + ' 节</div></div>' +
        (p >= 90 ? '<span class="pill">已读</span>' : p > 0 ?
          '<span class="pill g">' + p + '%</span>' : '<span style="color:var(--ink3)">›</span>') +
        '</div>' + (p > 0 && p < 90 ? '<div class="bar"><i style="width:' + p + '%"></i></div>' : '') +
        '</div>';
    });
    box.innerHTML = html;
    $$('[data-ch]', box).forEach(function (el) {
      el.onclick = function () { show('chapter', +el.dataset.ch); };
    });
  });
};

"""
s = s[:a] + new_course + s[b:]
s = s.replace("$('#ttl').textContent = '第' + c.n + '章 · ' + c.title;", "$('#ttl').textContent = c.title;")
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
h = h.replace('theme-color" content="#1f5673"', 'theme-color" content="#5b3a29"')
io.open(p, 'w', encoding='utf-8').write(h)

h = h.replace('学习路线与依赖图','学习路线').replace('先学哪章、后学哪章','初 → 中 → 高，按什么顺序学')
io.open(p, 'w', encoding='utf-8').write(h)
# manifest
p = os.path.join(ROOT, 'manifest.json')
m = io.open(p, encoding='utf-8').read().replace('命理精讲', '盲派八字').replace('#1f5673', '#5b3a29')
io.open(p, 'w', encoding='utf-8').write(m)
print('patched')
