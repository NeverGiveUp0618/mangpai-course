p = '_patch_app.py'
s = open(p).read()
if 'addReadToggle' not in s:
    marker = "io.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html"
    add = r'''# ---- 章节/专题阅读进度：不再滚动自动记，改为手动「标记为已读」 ----
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
'''
    s = s.replace(marker, add + marker, 1)
    open(p, 'w').write(s)
print('ok')
