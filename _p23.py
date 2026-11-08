import re, io, os, json

# ---------- 1) mdlite：render_chart 支持大运行 ----------
p = 'mdlite.py'
s = open(p).read()
if 'dayun=None' not in s:
    old = s[s.index("def render_chart(gan, zhi, label=''):"):s.index("_GAN = '甲乙丙丁戊己庚辛壬癸'")]
    new = '''def render_chart(gan, zhi, label='', dayun=None):
    """四柱盘的统一 HTML。app.js 里的吸顶条用同一套结构与 class。dayun＝['甲辰','乙巳',…] 时下面加一行大运色牌。"""
    cols = ''.join(
        '<div class="c%s"><div class="p">%s</div>%s%s</div>'
        % (' day' if k == 2 else '', p, gz_span(gan[k], 'a'), gz_span(zhi[k], 'b'))
        for k, p in enumerate(_PILLARS))
    lb = ('<span class="lb">%s造</span>' % _html.escape(label)) if label else ''
    dy = ''
    if dayun:
        dy = '<div class="dys"><span class="lb">运</span>%s</div>' % ''.join(
            '<div class="c">%s%s</div>' % (gz_span(x[0], 'a'), gz_span(x[1], 'b')) for x in dayun)
    return '<div class="ichart">%s<div class="cols">%s</div>%s</div>' % (lb, cols, dy)


'''
    s = s.replace(old, new, 1)
    open(p, 'w').write(s)

# ---------- 2) build_mp：大运合并进盘 ----------
p = 'build_mp.py'
b = open(p).read()
if 'def parse_dayun' not in b:
    b = b.replace("def write_js(name, var, obj):", '''def parse_dayun(text):
    """从「大运：甲辰 乙巳 …」里取出合法的干支对（阴阳同性），连续 ≥3 个才算。"""
    ps = re.findall(r'([%s])([%s])' % (GAN, ZHI), text)
    out = [g + z for g, z in ps if (GAN.index(g) - ZHI.index(z)) % 2 == 0]
    return out[:12] if len(out) >= 3 else None


def merge_dayun(html):
    """把盘后紧跟的「大运：…」段落并进盘里（色牌一行）。"""
    pat = re.compile(r'(<div class="ichart">(?:(?!<div class="ichart">).)*?</div></div>)\\s*<p>(?:<strong>)?大运[：:](.*?)</p>', re.S)

    def rep(m):
        dy = parse_dayun(re.sub(r'<[^>]+>', '', m.group(2)))
        if not dy:
            return m.group(0)
        chips = ''.join('<div class="c"><span class="a w-%s">%s</span><span class="b w-%s">%s</span></div>' % (
            WXC[x[0]], x[0], WXC[x[1]], x[1]) for x in dy)
        return m.group(1)[:-6] + '<div class="dys"><span class="lb">运</span>%s</div></div>' % chips
    return pat.sub(rep, html)


def write_js(name, var, obj):''', 1)
    b = b.replace("GAN = '甲乙丙丁戊己庚辛壬癸'\nZHI = '子丑寅卯辰巳午未申酉戌亥'\nWX =", "GAN = '甲乙丙丁戊己庚辛壬癸'\nZHI = '子丑寅卯辰巳午未申酉戌亥'\nWXC = {**{c: 'mu' for c in '甲乙寅卯'}, **{c: 'huo' for c in '丙丁巳午'}, **{c: 'tu' for c in '戊己辰戌丑未'}, **{c: 'jin' for c in '庚辛申酉'}, **{c: 'shui' for c in '壬癸亥子'}}\nWX =", 1)
    # build_doc 里合并
    b = b.replace("    html = md2html(s, heading_offset=0, collect_headings=heads, manual=False)\n    d = {", "    html = merge_dayun(md2html(s, heading_offset=0, collect_headings=heads, manual=False))\n    d = {", 1)
    # 命例：解析大运进 charts
    b = b.replace("        day = gan[2]\n        m = MARK.search(body)", "        day = gan[2]\n        dyl = None\n        for ln in ((c.get('dayun') or '') + '\\n' + body).split('\\n'):\n            if ln.strip().startswith('大运'):\n                dyl = parse_dayun(ln)\n                if dyl:\n                    break\n        m = MARK.search(body)", 1)
    b = b.replace("chai = ('<p><strong>%s日主</strong></p>' % day) + render_chart(gan, zhi, sex) +", "chai = ('<p><strong>%s日主</strong></p>' % day) + render_chart(gan, zhi, sex, dyl) +", 1)
    b = b.replace("'charts': [{'g': sex, 'gan': gan, 'zhi': zhi, 'label': ''}],", "'charts': [dict({'g': sex, 'gan': gan, 'zhi': zhi, 'label': ''}, **({'dy': dyl} if dyl else {}))],", 1)
    open(p, 'w').write(b)

# ---------- 3) app：命例吸顶盘加大运行 ----------
p = '_patch_app.py'
a = open(p).read()
if 'c.dy' not in a:
    marker = "io.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html"
    add = r'''old = "          gz(c.gan[i], 'a') + gz(c.zhi[i], 'b') + '</div>';\n      }).join('') + '</div></div>';"
new = "          gz(c.gan[i], 'a') + gz(c.zhi[i], 'b') + '</div>';\n      }).join('') + '</div>' +\n      (c.dy ? '<div class=\"dys\"><span class=\"lb2\">运</span>' + c.dy.map(function (x) { return '<div class=\"c\">' + gz(x.charAt(0), 'a') + gz(x.charAt(1), 'b') + '</div>'; }).join('') + '</div>' : '') + '</div>';"
assert old in s, 'sticky pattern'
s = s.replace(old, new, 1)
'''
    a = a.replace(marker, add + marker, 1)
    open(p, 'w').write(a)

# ---------- 4) CSS（新站）：去日柱框、大运行 ----------
p = 'style.css'
c = open(p).read()
c = c.replace(".doc .ichart .c.day,.sticky-chart .c.day{background:none; box-shadow:none; border-radius:10px; outline:2px solid var(--indigo2); outline-offset:1px}",
              ".doc .ichart .c.day,.sticky-chart .c.day{background:none; box-shadow:none; outline:none}")
if '.dys' not in c:
    c += '''
/* 大运行：盘下面一排色牌，可横滑 */
.doc .ichart{flex-wrap:wrap}
.doc .ichart .dys,.sticky-chart .dys{flex:1 0 100%; display:flex; align-items:center; gap:5px; overflow-x:auto; -webkit-overflow-scrolling:touch; margin-top:5px; padding-top:5px; border-top:1px dashed var(--line)}
.sticky-chart .grp{flex-wrap:wrap}
.doc .ichart .dys .lb,.sticky-chart .dys .lb2{flex:0 0 auto; font-size:11px; color:var(--ink3); font-weight:600; letter-spacing:1px; writing-mode:horizontal-tb}
.doc .ichart .dys .c,.sticky-chart .dys .c{flex:0 0 auto; text-align:center; min-width:26px}
.doc .ichart .dys .a,.doc .ichart .dys .b,.sticky-chart .dys .a,.sticky-chart .dys .b{width:25px; height:25px; line-height:25px; font-size:14px; border-radius:7px}
'''
open(p, 'w').write(c)
print('ok')
