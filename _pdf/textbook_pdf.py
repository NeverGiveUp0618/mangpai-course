# -*- coding: utf-8 -*-
"""盲派八字教材 → PDF（A4，朱砂檀香配色，每章后带习题）。

用法：python3 _pdf/textbook_pdf.py [--only 初级] [--out 路径]
做法：复用站点的 mdlite/build_mp 渲染教材 markdown（含色牌盘、大运同排、讲解手册式编号标题），
      拼成一份 HTML，再用无头 Chrome 打印成 PDF。习题＝章末自带的「思考题（含答案）」＋章节自测选择题（答案附后）。
"""
import os, re, sys, io, json, subprocess, html as H, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import build_mp as B  # noqa: E402

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
OUTDIR = os.path.abspath(os.path.join(ROOT, '..', '..', '学习册'))
LEVELS = ['初级', '中级', '高级', '专题']
PART_INTRO = {
    '初级': '入门：体系总览、宫位与十神、合冲穿刑破的作用方式、做功与应期入门。',
    '中级': '进阶：天道阴阳五行体用、干支象义、虚实与自合、正局反局、应期，以及财、官、婚、学历、牢狱专辑。',
    '高级': '深化：合冲穿刑破的深论、体用宾主、能量效率、正反局进阶、大运流年，以及婚姻、职业象法的高级断法。',
    '专题': '补充：由答疑与断例整理的专题，学到对应主题、遇到具体问题时再读。',
}
LETTERS = 'ABCDEFGH'


def load_js(name):
    s = io.open(os.path.join(ROOT, 'data', name), encoding='utf-8').read()
    return json.loads(s[s.find('=') + 1:].rstrip().rstrip(';'))


def chapters():
    """按站内同样的顺序列出教材章：[(level, idx, title, path)]。"""
    out = []
    for lv in LEVELS:
        d = os.path.join(ROOT, 'content', '教材', lv)
        fs = [f for f in os.listdir(d) if re.match(r'^\d+-.*\.md$', f)]
        fs.sort(key=B.tb_key)
        for i, f in enumerate(fs, 1):
            p = os.path.join(d, f)
            m = re.match(r'^(\d+)-(.*)\.md$', f)
            first = io.open(p, encoding='utf-8').read().split('\n', 1)[0].lstrip('# ').strip()
            out.append((lv, i, first or m.group(2), p))
    return out


def st_map():
    try:
        d = load_js('data-st.js')
    except Exception:
        return {}
    return {(c['level'], c['title']): c['qs'] for c in d['chapters']}


def open_details(h):
    h = re.sub(r'<details\b([^>]*)>', r'<details open\1>', h)
    return h


def mcq_html(qs):
    if not qs:
        return ''
    out = ['<section class="quiz"><h3 class="qh">章节自测 · 选择题</h3>']
    keys = []
    for i, q in enumerate(qs, 1):
        ans = int(q.get('ans', 0))
        keys.append('%d%s' % (i, LETTERS[ans]))
        out.append('<div class="q"><p class="qt"><b>%d.</b> %s</p><ol class="opts">%s</ol></div>' % (
            i, H.escape(q['q']), ''.join('<li><span class="ol">%s</span>%s</li>' % (LETTERS[k], H.escape(o)) for k, o in enumerate(q['opts']))))
    exps = ''.join('<li><b>%d%s</b>　%s</li>' % (i, LETTERS[int(q.get('ans', 0))], H.escape(q.get('exp') or '')) for i, q in enumerate(qs, 1))
    out.append('<div class="key"><b>参考答案</b>：%s<ol class="exps">%s</ol></div></section>' % ('　'.join(keys), ''))
    out[-1] = out[-1].replace('<ol class="exps"></ol>', '<ul class="exps">%s</ul>' % exps)
    return ''.join(out)


def renumber(h):
    """章末习题：每题被拆成 <ol><li>题</li></ol> + <details>答案</details>，序号会都变成 1，这里按小节连续编号。"""
    out, k, last = [], 0, 0
    for part in re.split(r'(<h[23][^>]*>)', h):
        if re.match(r'<h[23]', part):
            k = 0
        def rep(m):
            nonlocal k
            k += 1
            return '<ol start="%d"><li>' % k if k > 1 else m.group(0)
        part = re.sub(r'<ol><li>(?=(?:(?!</li>).)*</li></ol>\s*<details)', rep, part, flags=re.S)
        out.append(part)
    return ''.join(out)


def chapter_html(lv, idx, title, path, st):
    s = B.read(path)
    s = re.sub(r'^#\s+.*?\n', '', s, count=1)
    d = B.build_doc(path, 'x%s%d' % (lv, idx), idx, title, {}, manual=True)
    body = renumber(open_details(d['html']))
    body = re.sub(r'\sdata-raw="[^"]*"', '', body)
    cid = 'ch-%s-%d' % (lv, idx)
    head = '<header class="chead"><div class="ck">%s · 第 %d 章</div><h1>%s</h1></header>' % (lv, idx, H.escape(title))
    return '<article class="chap" id="%s">%s<div class="doc">%s</div></article>' % (cid, head, body)


CSS = u'''
@page { size: A4; margin: 18mm 17mm 21mm 17mm; background: #fbf6ec;
  @bottom-center { content: counter(page); font-family: "Songti SC", serif; font-size: 10pt; color: #8a6a4b; }
  @bottom-left { content: "盲派八字 · 教材"; font-family: "Songti SC", serif; font-size: 9pt; color: #b09a82; }
}
@page :first { margin: 0; @bottom-center { content: none; } @bottom-left { content: none; } }
:root{ --paper:#fbf6ec; --ink:#2b2622; --muted:#6f6254; --h:#7b3a2c; --accent:#b4842f; --line:#dccfb6; --soft:#f2e8d3;
  --wx-mu:#3d7a4a; --wx-huo:#c0452f; --wx-tu:#9a6b2f; --wx-jin:#b89a2e; --wx-shui:#2f5f9a; }
*{box-sizing:border-box}
html{background:#fff}
body{margin:0;font-family:"Songti SC","STSong",serif;font-size:13pt;line-height:1.85;color:var(--ink);background:var(--paper);
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
p{margin:.45em 0;text-align:justify;orphans:2;widows:2}
strong,b{color:var(--h)}
/* 封面 */
.cover{height:297mm;page-break-after:always;display:flex;flex-direction:column;justify-content:center;padding:0 24mm;
  background:linear-gradient(160deg,#fbf6ec 0%,#f2e4c8 100%);position:relative}
.cover:before{content:"";position:absolute;left:14mm;top:14mm;right:14mm;bottom:14mm;border:1.2pt solid var(--accent);border-radius:3mm}
.cover .kk{letter-spacing:.6em;color:var(--accent);font-size:13pt;margin-bottom:10mm}
.cover h1{font-family:"Kaiti SC","STKaiti",serif;font-size:50pt;line-height:1.25;margin:0 0 6mm;color:var(--h);letter-spacing:.12em}
.cover .sub{font-size:17pt;color:var(--muted);margin-bottom:18mm}
.cover .meta{font-size:12pt;color:var(--muted);line-height:2}
.cover .seal{position:absolute;right:26mm;bottom:30mm;width:26mm;height:26mm;border:2pt solid #b23a2b;color:#b23a2b;display:grid;place-items:center;
  font-family:"Kaiti SC",serif;font-size:19pt;line-height:1.2;text-align:center;border-radius:2mm;transform:rotate(-6deg)}
/* 目录 */
.toc{page-break-after:always}
.toc h2{font-family:"Kaiti SC",serif;font-size:26pt;color:var(--h);text-align:center;margin:8mm 0 8mm;letter-spacing:.3em}
.toc .part{font-family:"Kaiti SC",serif;font-size:17pt;color:var(--h);margin:7mm 0 2mm;padding-bottom:1mm;border-bottom:1pt solid var(--accent)}
.toc .part small{font-size:10.5pt;color:var(--muted);font-family:"Songti SC",serif;margin-left:3mm}
.toc ol{margin:0;padding:0;list-style:none;columns:2;column-gap:10mm}
.toc li{font-size:11.5pt;line-height:1.75;break-inside:avoid;color:var(--ink)}
.toc li a{color:inherit;text-decoration:none}
.toc li i{font-style:normal;color:var(--accent);display:inline-block;width:2.2em}
/* 分部页 */
.partpage{height:250mm;page-break-before:always;page-break-after:always;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center}
.partpage h1{font-family:"Kaiti SC",serif;font-size:62pt;color:var(--h);letter-spacing:.3em;margin:0 0 8mm;padding-left:.3em}
.partpage p{font-size:14pt;color:var(--muted);max-width:120mm;text-align:center}
.partpage .rule{width:40mm;height:1.4pt;background:var(--accent);margin:0 0 8mm}
/* 章 */
.chap{page-break-before:always}
.chead{margin:0 0 7mm;padding-bottom:4mm;border-bottom:1.4pt solid var(--accent)}
.chead .ck{color:var(--accent);letter-spacing:.35em;font-size:11.5pt;margin-bottom:2mm}
.chead h1{font-family:"Kaiti SC","STKaiti",serif;font-size:27pt;line-height:1.3;margin:0;color:var(--h)}
.doc h2{font-family:"Kaiti SC",serif;font-size:18pt;color:var(--h);margin:8mm 0 3mm;line-height:1.4;page-break-after:avoid;
  padding:1.2mm 0 1.2mm 3.5mm;border-left:2.6pt solid var(--accent);background:linear-gradient(90deg,var(--soft),transparent)}
.doc h3{font-family:"Kaiti SC",serif;font-size:15pt;color:#8e4a37;margin:6mm 0 2mm;page-break-after:avoid}
.doc h4{font-size:13.5pt;color:var(--h);margin:4mm 0 1mm;page-break-after:avoid}
.mhn{display:inline-block;min-width:1.55em;height:1.55em;line-height:1.55em;text-align:center;border-radius:50%;background:var(--h);color:#fff;
  font-family:"Songti SC",serif;font-size:.72em;margin-right:.55em;vertical-align:.08em}
h3 .mhn{background:var(--accent);border-radius:1mm;padding:0 .35em;min-width:2em}
.doc ul,.doc ol{margin:.4em 0 .6em;padding-left:1.5em}
.doc li{margin:.18em 0}
blockquote{margin:3mm 0;padding:2.5mm 4mm;background:var(--soft);border-left:2.4pt solid var(--accent);border-radius:0 2mm 2mm 0;font-size:12.5pt;page-break-inside:avoid}
blockquote p{margin:.25em 0}
.tw{margin:3mm 0;overflow:visible}
table{border-collapse:collapse;width:100%;font-size:11.5pt;line-height:1.6}
th,td{border:.6pt solid var(--line);padding:1.4mm 2.2mm;vertical-align:top}
th{background:#ecdfc3;color:var(--h);font-weight:700}
tr{page-break-inside:avoid}
.pill{display:inline-block;padding:0 2.5mm;border-radius:3mm;background:#ecdfc3;color:var(--h);font-size:10.5pt}
/* 命盘 */
.ichart{display:flex;flex-wrap:nowrap;align-items:flex-start;gap:3mm;margin:4mm 0;padding:3mm 4mm;border:.6pt solid var(--line);border-radius:2.5mm;
  background:#fff9ee;page-break-inside:avoid;width:max-content;max-width:100%}
.ichart .lb{align-self:center;font-family:"Kaiti SC",serif;color:var(--h);font-size:12.5pt;margin-right:1mm}
.ichart .cols{display:flex;gap:2mm}
.ichart .c{text-align:center;line-height:1}
.ichart .p{font-size:9.5pt;color:var(--muted);margin-bottom:1mm;line-height:1.2}
.ichart .a,.ichart .b{display:block;width:9mm;height:9mm;line-height:9mm;margin:1mm auto 0;border-radius:2mm;font-size:15pt;font-weight:700;text-align:center;
  background:#f6efe0;box-shadow:inset 0 0 0 .6pt var(--line)}
.ichart .dys{display:flex;gap:1.6mm;margin-left:2mm;padding-left:4mm;border-left:.8pt dashed #c9b790;align-items:flex-start}
.ichart .dys .lb{align-self:center;font-size:10.5pt;margin:0 1mm 0 0}
.ichart .dys .a,.ichart .dys .b{width:8.2mm;height:8.2mm;line-height:8.2mm;font-size:13pt}
.w-mu{color:var(--wx-mu)!important;background:#e3efdc!important}.w-huo{color:var(--wx-huo)!important;background:#f7ded6!important}
.w-tu{color:var(--wx-tu)!important;background:#efe0c4!important}.w-jin{color:var(--wx-jin)!important;background:#f3ebc4!important}
.w-shui{color:var(--wx-shui)!important;background:#dbe7f5!important}
/* 习题 */
details{margin:2.5mm 0 3.5mm;padding:2mm 3.5mm;background:#f7efdd;border-left:2.2pt solid #c98f3b;border-radius:0 2mm 2mm 0;page-break-inside:avoid;font-size:12.5pt}
details summary{font-weight:700;color:#8e4a37;list-style:none;font-size:11.5pt;letter-spacing:.1em}
details summary::-webkit-details-marker{display:none}
.quiz{margin-top:9mm;padding-top:4mm;border-top:1.2pt dashed var(--accent)}
.quiz .qh{font-family:"Kaiti SC",serif;font-size:17pt;color:var(--h);margin:0 0 3mm}
.q{margin:3mm 0;page-break-inside:avoid}
.qt{margin:0 0 1mm;font-size:13pt}
.opts{list-style:none;margin:0;padding:0 0 0 1.4em}
.opts li{margin:.5mm 0;font-size:12.2pt;line-height:1.7}
.opts .ol{display:inline-block;width:1.5em;color:var(--accent);font-weight:700}
.key{margin-top:4mm;padding:3mm 4mm;background:var(--soft);border-radius:2mm;font-size:11.8pt;page-break-inside:avoid}
.key b{color:var(--h)}
.exps{margin:2mm 0 0;padding-left:0;list-style:none;font-size:11pt;line-height:1.7;color:var(--muted)}
.exps li{margin:1mm 0}
.src-line,.src{font-size:10.5pt;color:var(--muted)}
'''


def build(only=None, out=None):
    st = st_map()
    chs = chapters()
    if only:
        chs = [c for c in chs if c[0] == only]
    parts = []
    toc = ['<section class="toc"><h2>目　录</h2>']
    cur = None
    body = []
    for lv, idx, title, path in chs:
        if lv != cur:
            if cur is not None:
                toc.append('</ol>')
            toc.append('<div class="part">%s<small>%s</small></div><ol>' % (lv, H.escape(PART_INTRO[lv])))
            body.append('<section class="partpage"><div class="rule"></div><h1>%s</h1><p>%s</p></section>' % (lv, H.escape(PART_INTRO[lv])))
            cur = lv
        toc.append('<li><a href="#ch-%s-%d"><i>%d</i>%s</a></li>' % (lv, idx, idx, H.escape(title)))
        body.append(chapter_html(lv, idx, title, path, st))
    toc.append('</ol></section>')
    today = datetime.date.today().strftime('%Y年%m月%d日')
    cover = ('<section class="cover"><div class="kk">学　习　册</div><h1>盲派八字<br>教材</h1><div class="sub">初级 · 中级 · 高级 · 专题　｜　每章附习题</div>'
             '<div class="meta">第一版（试读）<br>整理自段建业系盲派资料 · 学习自用<br>%s</div><div class="seal">盲派<br>八字</div></section>' % today)
    htm = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>盲派八字教材</title><style>%s</style></head><body>%s%s%s</body></html>' % (
        CSS, cover, ''.join(toc), ''.join(body))
    tmp = os.path.join(HERE, '_print.html')
    io.open(tmp, 'w', encoding='utf-8').write(htm)
    os.makedirs(OUTDIR, exist_ok=True)
    out = out or os.path.join(OUTDIR, '盲派八字教材 · 第一版%s.pdf' % ('（%s）' % only if only else ''))
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--no-pdf-header-footer', '--no-sandbox',
           '--virtual-time-budget=60000', '--print-to-pdf=' + out, 'file://' + tmp]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)
    print('chapters', len(chs), '->', out, round(os.path.getsize(out) / 1e6, 1), 'MB')
    return out


if __name__ == '__main__':
    only = None; out = None
    a = sys.argv[1:]
    if '--only' in a:
        only = a[a.index('--only') + 1]
    if '--out' in a:
        out = a[a.index('--out') + 1]
    build(only, out)
