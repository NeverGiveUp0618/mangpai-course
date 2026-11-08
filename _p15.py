p = '_patch_app.py'
s = open(p).read()
if 'decorateGap' not in s:
    marker = "io.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html"
    add = r'''# ---- 「我没学过」：掌握勾选 + 相关命例 ----
s = s.replace("  lvopen: 'mp_course_lvopen',", "  lvopen: 'mp_course_lvopen',\n  gap: 'mp_course_gap',", 1)
GAPTAGS = "['应期','应期','体用','桃花','墓库','墓库','穿','','体用','反局','体用','桃花']"
dec = """
var GAP_TAGS = %s;
function decorateGap() {
  var done = ls(K.gap, {});
  var hs = $$('#noteBody h3').filter(function (h) { return /^\\\\d+\\\\./.test(h.textContent.trim()); });
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
'''
    s = s.replace(marker, add + marker, 1)
    s = s.replace('<div class="muted" style="margin-top:2px">和你之前学的对照：哪些没讲过、在哪章读、哪些口径不同</div>', '<div class="muted" style="margin-top:2px" id="gapHint">和你之前学的对照：哪些没讲过、在哪章读、哪些口径不同</div>')
    open(p, 'w').write(s)
print('ok')
