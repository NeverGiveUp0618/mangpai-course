p = '_patch_app.py'
s = open(p).read()
if 'searchRaw' not in s:
    marker = "io.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html"
    add = r'''old = "    r[0].forEach(function (c) { scan(c.text, '第' + c.n + '章 · ' + c.title, 'chapter', c.n); });"
new = """    var rawMore = 0;
    r[0].forEach(function (c) {
      if (c.raw && !searchRaw) {
        var okAll = true; for (var t = 0; t < rest.length; t++) if (c.text.indexOf(rest[t]) < 0) okAll = false;
        if (okAll) { var at = -1; while ((at = c.text.indexOf(main, at + 1)) >= 0) rawMore++; }
        return;
      }
      scan(c.text, (c.raw ? '原稿 · ' : '') + c.title, 'chapter', c.n);
    });"""
assert old in s
s = s.replace(old, new, 1)
s = s.replace("function doSearch() {", "var searchRaw = false;\nfunction doSearch() {", 1)
hint = """    var rawHint = (!searchRaw && rawMore) ? '<div class="hit" id="rawHit"><b>原稿讲义里另有 ' + rawMore + ' 处</b><p>默认只搜教材与专题（原稿是逐字整理、内容与教材重叠）。点这里连原稿一起搜。</p></div>' : '';
    function bindRaw() { var e = $('#rawHit'); if (e) e.onclick = function () { searchRaw = true; doSearch(); }; }
"""
s = s.replace("    if (!hits.length) {\n      box.innerHTML = '<div class=\"empty\">没找到'", hint + "    if (!hits.length) {\n      box.innerHTML = '<div class=\"empty\">没找到'", 1)
s = s.replace("                     : '「' + esc(kw) + '」') + '</div>';\n      return;", "                     : '「' + esc(kw) + '」') + '</div>' + rawHint;\n      bindRaw();\n      return;", 1)
s = s.replace("          '<p>' + h.snip + '</p></div>';\n      }).join('');", "          '<p>' + h.snip + '</p></div>';\n      }).join('') + rawHint;\n    bindRaw();", 1)
s = s.replace("function doSearch() {", "function doSearch() {", 1)
'''
    # 这些替换应作用于 app.js 文本变量 s —— 写成补丁代码块插到写盘之前
    s = s.replace(marker, add + marker, 1)
    open(p, 'w').write(s)
print('ok')
