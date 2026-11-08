p = '_patch_app.py'
s = open(p).read()
if 'seenToggle' not in s:
    marker = "io.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html"
    add = r'''# ---- 命例学习标记：不再自动记，改为用户手动打 ----
a = s.index("function markSeenLater(n) {")
b = s.index("function ls(k, d) {", a)
s = s[:a] + "function markSeenLater(n) { clearTimeout(seenTimer); /* 学习标记由用户在命例页手动打，不再自动记 */ }\n" + s[b:]
old = "    $('#L4').innerHTML =\n      '<div class=\"row spread\" id=\"qnav\""
new = "    var isSeen = !!ls(K.seen, {})[it.n];\n    $('#L4').innerHTML =\n      '<div class=\"row\" style=\"margin:18px 0 0\"><button class=\"btn' + (isSeen ? ' pri' : '') + '\" id=\"seenToggle\" style=\"flex:1\">' + (isSeen ? '✓ 已学（点一下取消）' : '☐ 标记为已学') + '</button></div>' +\n      '<div class=\"row spread\" id=\"qnav\""
assert old in s
s = s.replace(old, new, 1)
s = s.replace("    $('#bList').onclick = function () { show('qlist', null); };", "    $('#seenToggle').onclick = function () {\n      var sv = ls(K.seen, {}); if (sv[it.n]) delete sv[it.n]; else sv[it.n] = Date.now(); save(K.seen, sv);\n      var on = !!sv[it.n]; this.className = 'btn' + (on ? ' pri' : ''); this.textContent = on ? '✓ 已学（点一下取消）' : '☐ 标记为已学';\n    };\n    $('#bList').onclick = function () { show('qlist', null); };", 1)
s = s.replace("['new', '没看过'],", "['new', '未标记已学'],", 1)
'''
    s = s.replace(marker, add + marker, 1)
    open(p, 'w').write(s)
print('ok')
