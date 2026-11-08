p='_patch_app.py'; s=open(p).read()
if 'gapCard' not in s:
    s=s.replace("# manifest","""h = h.replace('    <div class="card" id="progCard">', '''    <div class="card tap" id="gapCard">
      <div class="row spread">
        <div><b style="font-size:15px">🔎 我没学过 · 对照清单</b>
          <div class="muted" style="margin-top:2px">和你之前学的对照：哪些没讲过、在哪章读、哪些口径不同</div></div>
        <span style="color:var(--ink3)">&rsaquo;</span>
      </div>
    </div>

    <div class="card" id="progCard">''',1)
io.open(p, 'w', encoding='utf-8').write(h)
# manifest""",1)
    s=s.replace("io.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html","s = s.replace(\"/* 题库的可搜索全文。\", \"(function(){ var g = document.getElementById('gapCard'); if (g) g.onclick = function () { show('note', 1); }; })();\\n\\n/* 题库的可搜索全文。\", 1)\nio.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html",1)
    open(p,'w').write(s)
