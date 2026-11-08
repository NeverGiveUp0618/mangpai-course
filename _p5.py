p = '_patch_app.py'
s = open(p).read()
a = s.index('new_course = r"""')
b = s.index('"""\n', a + 20) + 4
new = r'''new_course = r"""RENDER.course = function () {
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
'''
s = s[:a] + new + s[b:]
s = s.replace("s = s.replace('bazi_course_', 'mp_course_')", "s = s.replace('bazi_course_', 'mp_course_')\ns = s.replace(\"counts: 'mp_course_counts',\", \"counts: 'mp_course_counts',\\n  lvopen: 'mp_course_lvopen',\")", 1)
open(p, 'w').write(s)
