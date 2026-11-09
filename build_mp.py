#!/usr/bin/env python3
"""content/**.md + _src/cases.json → data/*.js（与 bazi-course 同构的数据包）。

流程：python3 convert.py（原始文本→md/cases）→ python3 build_mp.py（md→data）。
data/*.js 全是产物，别手改。
"""
import os, re, io, json, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from mdlite import md2html, strip_md, render_chart  # noqa
from fmt import beautify, split_sent  # noqa

CONTENT = os.path.join(ROOT, 'content')
OUT = os.path.join(ROOT, 'data')
LEVELS = ['初级', '中级', '高级', '专题']

GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
WXC = {**{c: 'mu' for c in '甲乙寅卯'}, **{c: 'huo' for c in '丙丁巳午'}, **{c: 'tu' for c in '戊己辰戌丑未'}, **{c: 'jin' for c in '庚辛申酉'}, **{c: 'shui' for c in '壬癸亥子'}}
WX = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
YY = {g: (i % 2 == 0) for i, g in enumerate(GAN)}
BEN = dict(zip(ZHI, '癸己甲乙戊丙丁己庚辛戊壬'))
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}


def shishen(day, g):
    a, b = WX[day], WX[g]
    same = YY[day] == YY[g]
    if a == b:
        return '比肩' if same else '劫财'
    if SHENG[a] == b:
        return '食神' if same else '伤官'
    if KE[a] == b:
        return '偏财' if same else '正财'
    if KE[b] == a:
        return '七杀' if same else '正官'
    return '偏印' if same else '正印'


def parse_dayun(text):
    """从「大运：甲辰 乙巳 …」里取出合法的干支对（阴阳同性），连续 ≥3 个才算。"""
    ps = re.findall(r'([%s])([%s])' % (GAN, ZHI), text)
    out = [g + z for g, z in ps if (GAN.index(g) - ZHI.index(z)) % 2 == 0]
    return out[:12] if len(out) >= 3 else None


def merge_dayun(html):
    """把盘后紧跟的「大运：…」段落并进盘里（色牌一行）。"""
    pat = re.compile(r'(<div class="ichart">(?:(?!<div class="ichart">).)*?</div></div>)\s*<p>(?:<strong>)?大运[：:](.*?)</p>', re.S)

    def rep(m):
        dy = parse_dayun(re.sub(r'<[^>]+>', '', m.group(2)))
        if not dy:
            return m.group(0)
        chips = ''.join('<div class="c"><span class="a w-%s">%s</span><span class="b w-%s">%s</span></div>' % (
            WXC[x[0]], x[0], WXC[x[1]], x[1]) for x in dy)
        return m.group(1)[:-6] + '<div class="dys"><span class="lb">运</span>%s</div></div>' % chips
    return pat.sub(rep, html)


def write_js(name, var, obj):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    with io.open(p, 'w', encoding='utf-8') as f:
        f.write('window.%s=%s;\n' % (var, json.dumps(obj, ensure_ascii=False, separators=(',', ':'))))
    return os.path.getsize(p)


def read(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read()


def build_doc(path, ident, n, title, extra, manual=False):
    s = read(path)
    s = re.sub(r'^#\s+.*?\n', '', s, count=1)
    heads = []
    html = merge_dayun(md2html(s, heading_offset=0, collect_headings=heads, manual=manual))
    if manual:   # 讲解手册模式：标题带序号/重点标记，与命理精讲同款
        toc = [{'lv': lv, 't': t, 'a': a, 'st': st, 'm': 1 if mn else 0} for lv, t, a, st, mn in heads if lv <= 3]
    else:
        toc = [{'lv': lv, 't': t, 'a': a, 'st': 0, 'm': 0} for lv, t, a in heads if lv <= 3]
    d = {
        'id': ident, 'n': n, 'title': title, 'html': html,
        'toc': toc,
        'text': strip_md(s), 'chars': len(s),
    }
    d.update(extra)
    return d


def tb_key(fn):
    m = re.match(r'^(\d+)-(.*)$', fn)
    num = int(m.group(1)) if m else 0
    rest = m.group(2) if m else fn
    order = '上一二三四五六七八九十下'
    k = re.search(r'[（(]([上下一二三四五六七八九十])[）)]', rest)
    return (num, order.index(k.group(1)) if k else -1, rest)


PATHS = {}


def build_courses():
    books = json.load(io.open(os.path.join(ROOT, '_src', 'books.json'), encoding='utf-8'))
    bymap = {(b['level'], b['n']): b['book'] for b in books}
    docs, n = [], 1

    def add(path, title, lv, book, raw):
        nonlocal n
        PATHS['c%d' % n] = path
        docs.append(build_doc(path, 'c%d' % n, n, title, {'level': lv, 'book': book, 'raw': raw}, manual=(not raw)))
        n += 1

    def first_title(path, fallback):
        return read(path).split('\n', 1)[0].lstrip('# ').strip() or fallback

    for lv in LEVELS:
        # 教材（改写稿）
        d = os.path.join(CONTENT, '教材', lv)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d), key=tb_key):
                m = re.match(r'^(\d+)-(.+)\.md$', fn)
                if m:
                    add(os.path.join(d, fn), first_title(os.path.join(d, fn), m.group(2)), lv, '教材', False)
        # 原稿（逐字整理）——「专题」的原文在「查」里，不重复挂
        d = os.path.join(CONTENT, lv)
        if lv != '专题' and os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                m = re.match(r'^(\d+)-(.+)\.md$', fn)
                if m:
                    add(os.path.join(d, fn), first_title(os.path.join(d, fn), m.group(2)), lv,
                        bymap.get((lv, int(m.group(1))), ''), True)
    return docs


def build_qna():
    """笔记（我的提问与解答）：content/笔记/NN-标题.md；目录可以为空。"""
    docs, d = [], os.path.join(CONTENT, '笔记')
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            m = re.match(r'^(\d+)-(.+)\.md$', fn)
            if not m:
                continue
            title = read(os.path.join(d, fn)).split('\n', 1)[0].lstrip('# ').strip() or m.group(2)
            docs.append(build_doc(os.path.join(d, fn), 'q%d' % int(m.group(1)), int(m.group(1)), title, {}, manual='light'))
    return docs


def build_notes():
    docs, d = [], os.path.join(CONTENT, '专题')
    for k, fn in enumerate(sorted(os.listdir(d)), 1):
        m = re.match(r'^(\d+)-(.+)\.md$', fn)
        if not m:
            continue
        title = read(os.path.join(d, fn)).split('\n', 1)[0].lstrip('# ').strip() or m.group(2)
        docs.append(build_doc(os.path.join(d, fn), 'n%d' % k, k, title, {}))
    return docs


# ───────────────────────── 命例库 ─────────────────────────
TAGS = ['合', '冲', '穿', '刑', '破', '墓库', '入墓', '开库', '拱', '三合局', '暗合', '制', '化', '虚透', '带象', '禄', '原身', '羊刃',
        '官当财', '伤官', '食神', '桃花', '正局', '反局', '体用', '宾主', '换象', '借象', '应期', '空亡', '伏吟', '连根', '活木', '死木']
TAGKW = {'墓库': ['墓', '库'], '入墓': ['入墓'], '开库': ['开库', '冲开', '刑开'], '拱': ['拱'], '三合局': ['三合', '合局'], '暗合': ['暗合'],
         '制': ['制'], '化': ['化杀', '化用'], '虚透': ['虚透'], '带象': ['带象'], '禄': ['禄'], '原身': ['原身'], '羊刃': ['羊刃'],
         '官当财': ['当财'], '伤官': ['伤官'], '食神': ['食神'], '桃花': ['桃花'], '正局': ['正局'], '反局': ['反局'], '体用': ['体用'],
         '宾主': ['宾位', '主位'], '换象': ['换象'], '借象': ['借象'], '应期': ['应期', '运'], '空亡': ['空亡'], '伏吟': ['伏吟'],
         '连根': ['连根'], '活木': ['活木'], '死木': ['死木']}
BASIC = {'合': r'[天地]?干?合|六合|相合|合绊|合住', '冲': r'冲', '穿': r'穿', '刑': r'刑', '破': r'破'}

QA_RE = re.compile(r'(^|[\s。！？])(问|答|学员问|请问)[：:]|卜文|言明|博文|梅子|小月狐')
TOPIC_RULES = [
    ('正局反局', r'正局|反局'), ('财运', r'财命|财富|取财|求财|财运'), ('官运', r'官命|官运|官贵|当官|军官'),
    ('婚姻', r'婚|夫妻|独身|离婚|桃花|淫乱|配偶'), ('六亲', r'父母|六亲|子女|看寿|兄弟'),
    ('学历', r'学历'), ('牢狱', r'牢狱|犯罪'), ('疾病', r'疾病|病'), ('职业', r'职业|医生|老师|会计|口才|军官|盲人'),
    ('应期', r'应期|大运'), ('象法', r'象|类象'), ('作用方式', r'合|冲|穿|刑|破|墓|制|做功|体用|宾主|虚实|互通'),
]
TOPIC_ORDER = ['作用方式', '正局反局', '财运', '官运', '职业', '婚姻', '六亲', '学历', '牢狱', '疾病', '应期', '象法', '综合', '答疑讨论', '早期案例（用神口径）']


def topic_of(c):
    if c.get('early'):
        return '早期案例（用神口径）'
    if QA_RE.search(c.get('body', '')[:600]):
        return '答疑讨论'
    s = (c.get('chapter', '') + c.get('sec', '') + c.get('book', ''))
    for name, pat in TOPIC_RULES:
        if re.search(pat, s):
            return name
    return '综合'


def tags_of(text):
    out = []
    for t in TAGS:
        if t in BASIC:
            hit = re.search(BASIC[t], text)
        else:
            hit = any(k in text for k in TAGKW.get(t, [t]))
        if hit:
            out.append(t)
    return out[:8]


MARK = re.compile(r'(简历及解析[：:]|简历及简析[：:]|解析[：:]|分析[：:]|闲注[：:]|断[：:]|解[：:])')


def para_html(text):
    return md2html(beautify(text), heading_offset=0)


def quote_html(text):
    """老师讲解：排版成短段/列表，整体放进引用块（与命理精讲的「解」同款）。"""
    md = beautify(text)
    if not md:
        return ''
    return md2html('\n'.join(('> ' + l) if l.strip() else '>' for l in md.split('\n')), heading_offset=0)


def tidy(t):
    """去掉混进讲解里的大运/年份表格行、占位符和「分析：」之类的标签。"""
    t = t.replace('★§', ' ')
    t = re.sub(r'大运[：:\s]*(?:[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥][\s、，,]*){3,}', ' ', t)
    t = re.sub(r'\d+月\s*\d+日起运|岁数[\s\d.]+|年份[\s\d.]+|[（(]?\d+岁起运[）)]?', ' ', t)
    t = re.sub(r'(?<![\u4e00-\u9fff])(分析|闲注|解析|简历及解析|简历及简析|断|注)[：:]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip(' ，,；;：:')
    t = re.sub(r'^(?:运|岁|年)[，,]\s*', '', t)
    return t


def split_case(body):
    """返回 (标签, 断/简历 文字, 解 文字)。"""
    m = MARK.search(body)
    pre = body[:m.start()].strip() if m else ''
    label = '断'
    rest = body[m.end():].strip() if m else body.strip()
    if m and '简历' in m.group(0):
        label = '简历'
    if pre:
        return label, pre, rest
    sents = [x.strip() for x in split_sent(re.sub(r'\s+', ' ', rest)) if x.strip()]
    if len(sents) <= 1:
        return label, rest, ''
    face, k = '', 0
    while k < len(sents) and (len(face) < 28 or k == 0) and k < 2:
        face += sents[k]
        k += 1
    return label, face, ''.join(sents[k:])


_W = r'[\s  　]'


def _pairs_ok(stems, branches):
    out = [g + z for g, z in zip(stems, branches) if (GAN.index(g) - ZHI.index(z)) % 2 == 0]
    return out if len(out) == min(len(stems), len(branches)) and len(out) >= 3 else None


def strip_dayun(body):
    """去掉混进命例正文里的大运/起运年份/岁数残行；能还原成干支对的返回 dayun 列表，供画进盘里。"""
    G, Z = '[%s]' % GAN, '[%s]' % ZHI
    body = body.replace(chr(0x2028), '\n')
    # 文中任意位置的残留：年份串、「N岁运：6戊16丁…」、「大运：戊子 丁亥 …」、散开的单字干支串
    body = re.sub(r'(?:(?:1[89]|20)\d\d[\s\u00a0]*){3,}', ' ', body)
    body = re.sub(r'\d{1,2}岁(?:大)?运[：:]?[\s\u00a0]*(?:\d{1,3}[%s][\s\u00a0]*){3,}' % GAN, ' ', body)
    body = re.sub(r'(?:\d{1,2}岁(?:大)?运[：:]?)?(?:大运[：:；;]?)?(?:\d{1,3}\s*[%s]\s*){3,}(?:[%s戍]\s*){0,12}' % (GAN, ZHI), ' ', body)
    body = re.sub(r'(?:\d{1,3}岁\s*){4,}(?:止于[：:]?)?', ' ', body)
    body = re.sub(r'[\x00-\x08\x0b-\x1f]', '', body)
    body = re.sub(r'(?:始于|止于)[：:]', ' ', body)
    body = re.sub(r'(?:十神类象简表|腿脚\s*遗传宫).*$', '', body, flags=re.S)
    body = re.sub(r'=\s*\d+\s*\\\*\s*GB\d\s*[⑴-⒇①-⑩]?', ' ', body)
    body = re.sub(r'\d*\s*月\s*\d*\s*日起运|\d+岁\d*年?起运', ' ', body)
    body = re.sub(r'大运[：:；;]?(?:[\s\u00a0•·：:、，,\d%s%s戍]|日(?=[\s\d]))+' % (GAN, ZHI),
                  lambda m: ' ' if len(re.findall('[%s%s戍]' % (GAN, ZHI), m.group(0))) >= 6 else m.group(0), body)
    body = re.sub(r'(?:^|(?<=[\s：:]))(?:[乾坤][\s\u00a0]+)?(?:[%s%s戍][\s\u00a0]+){4,}[%s%s戍]?(?=[\s\u4e00-\u9fff]|$)' % (GAN, ZHI, GAN, ZHI), ' ', body, flags=re.M)
    lines = body.split('\n')
    out, dy, i = [], None, 0
    nz = lambda x: re.sub(_W, '', x)
    while i < len(lines):
        ln = lines[i]
        t = nz(ln)
        if not t:
            out.append(ln); i += 1; continue
        # 1 行首内联：「6癸 16壬 … 卯 寅 丑」或「大运：甲乙丙丁 辰巳午未」后面直接跟正文
        m = re.match(r'^(?:大运[：:；;]?)?((?:\d{1,3}%s[\s 　]*){3,}|(?:%s[\s 　]*){3,})((?:%s[\s 　]*){3,})' % (G, G, Z), ln.strip())
        if m:
            st = re.findall(G, m.group(1)); br = re.findall(Z, m.group(2))
            if len(st) == len(br):
                dy = dy or _pairs_ok(st, br)
                rest = ln.strip()[m.end():].strip()
                rest = re.sub(r'^[\d\s]+(?=[一-鿿])', '', rest) if re.match(r'^\d+\s*$', rest[:3]) else rest
                if rest:
                    out.append(rest)
                i += 1
                continue
        # 2 干支对一行：「大运 辛未 庚午 …  8月29日起运」「己未 戊午 …」
        m = re.match(r'^(?:大运[：:；;]?)?((?:%s%s)+)(?:\d+月\d+日起运|\d+岁.{0,6}起运|\d+[岁年].*)?$' % (G, Z), t)
        if m and len(m.group(1)) >= 6:
            ps = re.findall(r'(%s)(%s)' % (G, Z), m.group(1))
            dy = dy or _pairs_ok([a for a, b in ps], [b for a, b in ps])
            i += 1; continue
        # 3 年龄行：「1 11 21 …」「大运：5 15 25」「1岁 11岁」
        if re.match(r'^(?:大运[：:；;]?)?(?:\d{1,3}岁?)+$', t) and re.search(r'\d', t) and len(re.findall(r'\d+', ln)) >= 3:
            i += 1; continue
        # 4 年份行 / 始于 / 流年 / 起运
        if re.match(r'^(?:始于|起运|流年|年份|岁数)[：:]', t) or re.match(r'^(?:(?:1[89]|20)\d\d){3,}$', t) \
                or re.match(r'^\d+岁\d*年?起运', t) or re.match(r'^[甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]{4}.{0,3}\d+岁\d+年起运$', t):
            i += 1; continue
        # 5 「大运：10戊20己…」+ 下一行「64子74丑…」
        m = re.match(r'^大运[：:；;]?((?:\d{1,3}%s)+)$' % G, t)
        if m and i + 1 < len(lines):
            n2 = nz(lines[i + 1])
            if re.match(r'^(?:\d{1,3}%s)+$' % Z, n2) or re.match(r'^%s+$' % Z, n2):
                st = re.findall(G, m.group(1)); br = re.findall(Z, n2)
                if len(st) == len(br):
                    dy = dy or _pairs_ok(st, br)
                    i += 2; continue
        # 6 「大运：甲乙丙丁 辰巳午未」「大运 庚己戊丁 午巳辰卯」「大运：5 庚…」同行
        m = re.match(r'^大运\d*[：:]?\d*((?:%s)+)\d*((?:%s)+)\d*$' % (G, Z), t)
        if m and len(m.group(1)) == len(m.group(2)):
            dy = dy or _pairs_ok(list(m.group(1)), list(m.group(2)))
            i += 1; continue
        # 7 「大运：甲乙丙丁」+ 下一行「辰巳午未」
        m = re.match(r'^(?:大运[：:；;]?)?\d*((?:%s)+)\d*$' % G, t)
        if m and len(m.group(1)) >= 4 and i + 1 < len(lines):
            n2 = nz(lines[i + 1])
            if re.match(r'^(?:%s)+\d*$' % Z, n2) and len(re.findall(Z, n2)) == len(m.group(1)):
                dy = dy or _pairs_ok(list(m.group(1)), re.findall(Z, n2))
                i += 2; continue
        # 9 以「大运」开头的短行（OCR 残行，没有句读）
        if t.startswith('大运') and len(t) <= 42 and not re.search('[。，；！？]', t):
            m = re.findall(r'([%s])([%s])' % (GAN, ZHI), t)
            i += 1; continue
        # 8 孤立的纯干/纯支长串（运干运支行的残留）
        if re.match(r'^(?:%s){5,}$' % G, t) or re.match(r'^(?:%s){5,}$' % Z, t):
            i += 1; continue
        out.append(ln); i += 1
    return '\n'.join(out), dy


def build_quiz():
    cases = json.load(io.open(os.path.join(ROOT, '_src', 'cases.json'), encoding='utf-8'))
    best = {}
    for c in cases:
        body = c['body'].strip()
        if len(body) < 60:
            continue
        gan, zhi = c['gan'], c['zhi']
        if len(gan) != 4 or len(zhi) != 4 or any(x not in GAN for x in gan) or any(x not in ZHI for x in zhi):
            continue
        if c.get('bad'):   # skip_bad：存疑盘不收
            continue
        if body.count('╱') >= 3:      # 「流年╱大运☆」清单串盘的错乱段，无法还原
            continue
        # 正文里已经滑进下一例/下一节的内容：在「●乾造」「第N节」「●…组合」「例N.」处截断
        _cut = re.search(r'(?<=.)(?:[●•]\s*[乾坤]\s*造|第[一二三四五六七八九十]+节|●[^\n●]{2,14}(?:组合|看法|断法|判断)|\n\s*例\s*\d+[.．、])', body)
        if _cut and _cut.start() > 40:
            body = body[:_cut.start()].strip()
        key = (c['sex'], gan, zhi)
        c['body'] = body
        old = best.get(key)
        if old is None or (old.get('early') and not c.get('early')) or \
                (bool(old.get('early')) == bool(c.get('early')) and len(body) > len(old['body'])):
            best[key] = c
    uniq = list(best.values())
    items = []
    tagcount = {}
    for c in uniq:
        gan, zhi, sex, body = list(c['gan']), list(c['zhi']), c['sex'], c['body']
        day = gan[2]
        dyl = None
        for ln in ((c.get('dayun') or '') + '\n' + body).split('\n'):
            if ln.strip().startswith('大运'):
                dyl = parse_dayun(ln)
                if dyl:
                    break
        body, _dy2 = strip_dayun(body)
        dyl = dyl or _dy2
        if not dyl and c.get('dayun'):
            dyl = strip_dayun(c['dayun'])[1]
        label, face_t, jie = split_case(body)
        face_t, jie = tidy(face_t), tidy(jie)
        if len(re.sub(r'\s', '', face_t + jie)) < 20:      # 清完只剩残渣，没有可读内容 → 不收
            continue
        if len(re.sub(r'\s', '', face_t)) < 4 and jie:      # 题面只剩标签：拿解的头一两句当题面
            _ss = [x.strip() for x in split_sent(re.sub(r'\s+', ' ', jie)) if x.strip()]
            if len(_ss) >= 2:
                face_t, jie = _ss[0], ''.join(_ss[1:])
        jie = re.sub(r'^(简历及解析|简历及简析|解析|分析|解)[：:]', '', jie).strip()
        face_src = face_t
        sums = re.sub(r'[\s　]+', '', (face_t + ' ' + jie))
        GEN = re.compile(r'^(老师讲|分析|闲注|注|象|例|如|又如|此造|此人|该造|断|解|乾|坤|大运.*)$')
        sums2 = re.sub(r'(闲注|分析|断|解|注)[:：]', '，', sums)
        segs = [re.sub(r'^(此造是|此造为|此人是|此人为|此造|此人|该造|本造)', '', x) for x in re.split(r'[，。；：:、！？（）()\.\s]', sums2) if x]
        segs = [x for x in segs if sum(c in GAN + ZHI or c.isdigit() for c in x) <= len(x) * 0.4]
        segs = [x for x in segs if len(x) >= 5 and not GEN.match(x)]
        brief = segs[0] if segs else ''
        if len(brief) < 8 and len(segs) > 1:
            brief = brief + '，' + segs[1]
        brief = (brief[:20] or '命例')
        brief = re.sub(r'^[乾坤][：:造]*', '', brief)
        title = '%s造 %s%s日 · %s' % (sex, day, zhi[2], brief)
        ss_g = ' '.join('%s%s' % (p, shishen(day, g)) for p, g in zip('年月时', [gan[0], gan[1], gan[3]]))
        ss_z = ' '.join('%s%s' % (p, shishen(day, BEN[z])) for p, z in zip('年月日时', zhi))
        chai = ('<p><strong>%s日主</strong></p>' % day) + render_chart(gan, zhi, sex, dyl) + \
               '<p><strong>天干十神</strong>：%s</p><p><strong>地支（取本气）</strong>：%s</p>' % (ss_g, ss_z)
        face = '<p><strong>%s</strong>：</p>' % label + para_html(face_t)
        tags = tags_of(sums)
        if c.get('early'):
            tags = ['早期口径'] + tags
            face = '<p><span class="pill g">⚠️ 早期口径：出自《盲派批命案例集》，仍以用神、旺衰为核心，与成熟体系不同，对照阅读</span></p>' + face
        if c.get('bad'):
            tags = ['待校对'] + tags
            face += '<p><span class="pill g">⚠️ 此盘干支组合不合历法，疑识别或原稿笔误，待对照原件校对</span></p>'
        for t in tags:
            tagcount[t] = tagcount.get(t, 0) + 1
        topic = topic_of(c)
        items.append({
            'n': 0, 'title': title, 'tags': tags, 'star': 0,
            'chart': {'g': sex, 'gan': gan, 'zhi': zhi}, 'nCharts': 1,
            'charts': [dict({'g': sex, 'gan': gan, 'zhi': zhi, 'label': ''}, **({'dy': dyl} if dyl else {}))],
            'face': face, 'jieLabel': '解', 'jie': (quote_html(jie) if jie else '<p class="muted">原稿对这个盘只给了上面的断语，没有再展开讲解。可点「拆解」看十神与五行。</p>'), 'chai': chai, 'noAnswer': 0,
            'text': sums[:4000], 'topic': topic, 'seq': 0,
            '_src': '%s · %s' % (c.get('book', ''), c.get('chapter', '')),
        })
    # 按主题顺序排，再给连续号
    items.sort(key=lambda x: (TOPIC_ORDER.index(x['topic']), x['_src']))
    for i, it in enumerate(items, 1):
        it['n'] = i
        it['seq'] = i
        it['jie'] += '<p class="src-line"><span class="src">出处：%s</span></p>' % it.pop('_src').rstrip('：: ')
    topics = []
    for t in TOPIC_ORDER:
        k = sum(1 for x in items if x['topic'] == t)
        if k:
            topics.append({'name': t, 'n': k})
    intro = ('<h2 id="命例库">命例库</h2><blockquote><p><strong>这是什么</strong>：从初、中、高级讲义与专题里抽出来的带完整四柱的命例。'
             '遮住「解」自己先推，再对照。<br><strong>说明</strong>：同一盘在多册里出现时取最完整的一份；'
             '部分命例原资料只给了图片、没有文字盘，这里暂未收入（二期补）。</p></blockquote>')
    return {'intro': intro, 'items': items, 'tags': sorted(tagcount.items(), key=lambda x: -x[1]), 'topics': topics}


THEMES = [
    ('体系总览与宫位', ['盲派体系总览', '宫位取象'], ['天道、阴阳', '十神与宫位', '宫位类象', ], ['体用宾主']),
    ('十神与类象', ['十神类象'], ['干支类象', '宫位类象与十神'], ['宫位、十神、神煞类象深化', '干支象义']),
    ('干支与虚实', ['十天干', '干支配置'], ['十天干象义', '干支关系', '十二地支象义', '干支虚实'], []),
    ('合', ['合（一）', '合（二）', '合（三）'], ['地支作用'], ['天干五合与地支六合']),
    ('冲、穿、刑、破、墓', ['刑、破、害、墓', '冲、穿（一）', '冲、穿（二）'], [], ['三合、六冲']),
    ('做功与效率', ['做功方式'], ['象的应用'], ['能量效率']),
    ('正局与反局', ['基础问题'], ['正局与反局'], ['正局反局进阶']),
    ('入手与层次', ['入手方法', '补充答疑'], [], []),
    ('大运流年与应期', ['应期入门'], ['应期'], ['大运流年与应期']),
    ('财与官', [], ['财命专辑', '官命看法'], ['财命的高级断法', '官命、职业与学历']),
    ('婚姻', ['婚姻与看寿'], ['婚姻专辑'], ['婚姻宫', '恋爱同居', '男命多婚', '女命多婚', '婚外情', '包局婚姻', '配偶情况', '伤克配偶', '独身组合', '差婚姻']),
    ('六亲（父母）', [], [], ['父母死亡', '父母离异']),
    ('学历、牢狱与实战', [], ['学历与牢狱', '实战演示'], []),
        ('职业象法', [], [], ['职业象法']),
]


def _ref_clean(t):
    t = re.sub(r'[*`⭐⚠️💡]+', '', t or '').strip()
    t = re.sub(r'^[一二三四五六七八九十〇\d]+\s*[、.．·]\s*', '', t)
    head = re.split(r'[：:（(]', t)[0].strip()
    if len(head) >= 3:
        t = head
    return t.strip('　 ·—-')


def _is_pan_table(block):
    head = re.sub(r'[*\s]', '', block[0])
    cells = [c for c in head.split('|') if c]
    return all(x in cells for x in ('年', '月', '日', '时')) or any(c in ('年柱', '月柱', '日柱', '时柱') for c in cells)


def build_ref(courses):
    """速查：每章小结卡 + 口诀集 + 教材里的表格（非命盘）。内容源仍只有教材一处。"""
    sums, kous, tabs = [], [], []
    seen_k = set()
    for c in courses:
        if c['raw'] or c['id'] not in PATHS:
            continue
        md = read(PATHS[c['id']])
        lines = md.split('\n')
        # 小结：标题含「小结」的 ## 节，到下一个 ## 为止
        i = 0
        while i < len(lines):
            if re.match(r'^##\s+.*小结', lines[i]) and not lines[i].startswith('###'):
                j = i + 1
                while j < len(lines) and not (lines[j].startswith('## ') and not lines[j].startswith('###')):
                    j += 1
                body = '\n'.join(lines[i + 1:j]).strip()
                body = re.sub(r'<details>.*?</details>', '', body, flags=re.S)
                body = re.split(r'^(?:#{2,4}\s*|\*\*|\d+[.、]\s*\*\*)?(?:本章)?自测.*$', body, flags=re.M)[0].strip()
                if len(body) > 40:
                    sums.append({'n': c['n'], 'level': c['level'], 'title': c['title'], 'html': merge_dayun(md2html(body)), 'text': strip_md(body)})
                break
            i += 1
        # 口诀
        for ln in lines:
            m = re.match(r'^>?\s*\**口诀\**[：:]\s*\**(.+?)\**\s*$', ln.strip())
            if m:
                t = strip_md(m.group(1)).strip('「」 ')
                if len(t) >= 6 and t not in seen_k:
                    seen_k.add(t)
                    kous.append({'n': c['n'], 'level': c['level'], 'chapter': c['title'], 'text': t})
        # 表格
        h2 = h3 = ''
        i = 0
        while i < len(lines):
            ln = lines[i]
            mm = re.match(r'^##\s+(.*)$', ln)
            if mm and not ln.startswith('###'):
                h2, h3 = _ref_clean(mm.group(1)), ''
            mm = re.match(r'^###\s+(.*)$', ln)
            if mm:
                h3 = _ref_clean(mm.group(1))
            if ln.startswith('|'):
                st = i
                while i < len(lines) and lines[i].startswith('|'):
                    i += 1
                blk = lines[st:i]
                if len(blk) < 3 or _is_pan_table(blk):
                    continue
                lead = ''
                for j in range(st - 1, max(-1, st - 3), -1):
                    tt = lines[j].strip()
                    if not tt:
                        continue
                    if len(tt) <= 40 and not tt.startswith(('|', '>', '-', '#', '`', '<')):
                        lead = _ref_clean(tt)
                    break
                name = lead if 2 <= len(lead) <= 14 else (h3 or h2 or lead or c['title'])
                name = name if len(name) <= 28 else name[:27] + '…'
                tabs.append({'n': c['n'], 'level': c['level'], 'chapter': c['title'], 'sec': h3 or h2, 'name': name,
                             'html': md2html('\n'.join(blk)), 'text': strip_md('\n'.join(blk))})
                continue
            i += 1
    return {'sum': sums, 'kou': kous, 'tab': tabs}


TOPIC_CHAPTERS = {
    '作用方式': [('初级', '合（'), ('初级', '冲、穿'), ('初级', '刑、破'), ('初级', '做功方式'), ('中级', '地支作用'), ('中级', '象的应用'), ('高级', '天干五合与地支六合'), ('高级', '三合、六冲')],
    '正局反局': [('初级', '基础问题'), ('中级', '正局与反局'), ('高级', '正局反局进阶')],
    '财运': [('中级', '财命专辑'), ('高级', '财命的高级断法'), ('专题', '职业专题（一）')],
    '官运': [('中级', '官命看法'), ('高级', '官命、职业与学历'), ('专题', '职业专题（二）')],
    '职业': [('高级', '职业象法'), ('专题', '职业专题')],
    '婚姻': [('初级', '婚姻与看寿'), ('中级', '婚姻专辑'), ('高级', '婚姻宫'), ('高级', '男命多婚'), ('高级', '女命多婚'), ('高级', '婚外情'), ('高级', '包局婚姻'),
           ('高级', '配偶情况'), ('高级', '伤克配偶'), ('高级', '独身组合'), ('高级', '差婚姻'), ('专题', '婚姻问答')],
    '六亲': [('高级', '父母死亡'), ('高级', '父母离异'), ('专题', '伤官、六亲')],
    '学历': [('中级', '学历与牢狱')],
    '牢狱': [('中级', '学历与牢狱')],
    '疾病': [('专题', '疾病专题')],
    '应期': [('初级', '应期入门'), ('中级', '应期'), ('高级', '大运流年与应期'), ('专题', '应期与墓穿')],
    '象法': [('初级', '十神类象'), ('初级', '宫位取象'), ('中级', '干支类象'), ('中级', '宫位类象'), ('中级', '十天干象义'), ('中级', '十二地支象义'), ('初级', '十天干'), ('初级', '干支配置'), ('中级', '干支关系'), ('中级', '干支虚实'), ('专题', '象法与象的应用')],
    '综合': [('初级', '盲派体系总览'), ('初级', '入手方法')],
}


def chapters_of(courses, topic):
    out = []
    for lv, pre in TOPIC_CHAPTERS.get(topic, []):
        for c in courses:
            if not c['raw'] and c['level'] == lv and c['title'].startswith(pre) and c not in out:
                out.append(c)
    return out


def link_related(courses, quiz):
    """命例 → 相关教材章节（rel）；教材章节 → 相关命例（cases，≤8，优先带大运、讲解长的）。"""
    items = quiz['items']
    bytopic = {}
    for it in items:
        bytopic.setdefault(it['topic'], []).append(it)
    for t, its in bytopic.items():
        chs = chapters_of(courses, t)[:4]
        for it in its:
            it['rel'] = [{'n': c['n'], 't': c['title']} for c in chs]
    score = lambda it: (1 if it['charts'][0].get('dy') else 0, len(it['text']))
    for c in courses:
        if c['raw']:
            continue
        pool = []
        for t in TOPIC_CHAPTERS:
            if c in chapters_of(courses, t):
                pool.extend(bytopic.get(t, []))
        pool = sorted({id(x): x for x in pool}.values(), key=score, reverse=True)[:8]
        c['cases'] = [{'n': x['n'], 't': x['title']} for x in pool]


ST_RE = re.compile(r'(?:^|\n)\s*(?:\d+|[①②③④⑤⑥⑦⑧⑨⑩])[\.、．]?\s*(.+?)\n\s*<details>\s*<summary>[^<]*</summary>(.*?)</details>', re.S)


def build_selftest(courses):
    """把每章「自测」题＋折叠答案做成客观选择题：正确答案＋同章/同级其他题的答案作干扰项。"""
    import random
    chs = []
    for c in courses:
        if c['raw'] or c['id'] not in PATHS:
            continue
        md = read(PATHS[c['id']])
        qs = []
        for m in ST_RE.finditer(md):
            q = strip_md(m.group(1)).strip()
            a = strip_md(m.group(2)).strip()
            if 6 <= len(q) <= 120 and 6 <= len(a) <= 260:
                qs.append({'q': q, 'a': a})
        if qs:
            chs.append({'n': c['n'], 'level': c['level'], 'title': c['title'], 'qs': qs})
    lv_answers = {}
    for ch in chs:
        lv_answers.setdefault(ch['level'], []).extend(x['a'] for x in ch['qs'])
    for ch in chs:
        answers = [x['a'] for x in ch['qs']]
        for k, x in enumerate(ch['qs']):
            rnd = random.Random('%s-%d' % (ch['n'], k))
            own = [a for j, a in enumerate(answers) if j != k]
            rnd.shuffle(own)
            pool = own[:3]
            if len(pool) < 3:
                more = [a for a in lv_answers[ch['level']] if a != x['a'] and a not in pool]
                rnd.shuffle(more)
                pool += more[:3 - len(pool)]
            opts = pool + [x['a']]
            rnd.shuffle(opts)
            x['opts'] = opts
            x['ans'] = opts.index(x['a'])
            del x['a']
            x['exp'] = opts[x['ans']]
    return {'chapters': chs}


def build_outline(courses, notes, quiz):
    def find(lv, prefixes):
        out = []
        for pre in prefixes:
            for c in courses:
                if c['level'] == lv and not c['raw'] and c['title'].startswith(pre) and c not in out:
                    out.append(c)
        return out

    def links(cs):
        return '<br>'.join('<a class="chlink" data-ch="%d">%s</a>' % (c['n'], c['title']) for c in cs) or '—'
    h = ['<h1 id="学习路线">学习路线</h1>',
         '<blockquote><p><strong>怎么学</strong>：先读完初级（建立体系），再按需要进中级、高级；同一个主题在三级里是<strong>由浅入深</strong>的同一条线，下面按主题横向对照，一眼看到该主题三级各读哪几章。读完一章，回「练」里做对应主题的命例。</p></blockquote>',
         '<p><strong>收录范围</strong>：只收盲派体系<strong>成熟期</strong>的资料；早期仍用用神的口径只作对照（命例里标「早期口径」）。教材是改写整理稿，逐字原稿收在课程页各级下的「原稿讲义」里。</p>',
         '<h2 id="主题对照">按主题对照</h2>',
         '<div class="tw"><table><thead><tr><th>主题</th><th>初级</th><th>中级</th><th>高级</th></tr></thead><tbody>']
    for name, a, b2, c3 in THEMES:
        h.append('<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            name, links(find('初级', a)), links(find('中级', b2)), links(find('高级', c3))))
    h.append('</tbody></table></div>')
    zt = [c for c in courses if c['level'] == '专题' and not c['raw']]
    if zt:
        h.append('<h2 id="专题">专题（问答改写，按需查读）</h2><p>由论坛答疑、断例整理而成的补充专题，不在主线里；学到对应主题、或遇到具体问题时再读。</p><ul>' + ''.join('<li><a class="chlink" data-ch="%d">%s</a></li>' % (c['n'], c['title']) for c in zt) + '</ul>')
    h.append('<h2 id="顺序">建议顺序</h2><ol><li><strong>初级</strong>：按章顺序通读（18 章），重点是体系总览、宫位、十神、干支配置、合冲穿刑破墓、做功方式。</li>'
             '<li><strong>中级</strong>：先读「干支奥义」七章打牢象义，再读正局反局、应期、类象与象的应用，然后读财官婚学牢专辑；「专题」组是答疑改写的补充，遇到具体问题时再查读。</li>'
             '<li><strong>高级</strong>：先读作用方式深论、体用宾主与能量效率，再按需要读婚姻六亲与职业象法。</li></ol>')
    return ''.join(h)


def main():
    # 「我没学过」对照页随教材自动更新（读 ../bazi-course 只读）
    import subprocess
    g = os.path.join(ROOT, '_gap.py')
    if os.path.exists(g):
        subprocess.run([sys.executable, g], stdout=subprocess.DEVNULL, check=False)
    courses = build_courses()
    notes = build_notes()
    qna = build_qna()
    quiz = build_quiz()
    link_related(courses, quiz)
    ref = build_ref(courses)
    st = build_selftest(courses)
    meta = {
        'name': '盲派八字', 'built': time.strftime('%Y-%m-%d %H:%M'),
        'counts': {'qna': len(qna), 'selftest': sum(len(c['qs']) for c in st['chapters']), 'course': sum(1 for c in courses if not c['raw']) or len(courses), 'rawCourse': sum(1 for c in courses if c['raw']), 'notes': len(notes), 'quiz': len(quiz['items']),
                   'quizChart': len(quiz['items']), 'quizChai': len(quiz['items'])},
        'levels': [{'name': lv, 'n': sum(1 for c in courses if c['level'] == lv and not c['raw']), 'raw': sum(1 for c in courses if c['level'] == lv and c['raw'])} for lv in LEVELS],
        'outline': build_outline(courses, notes, quiz),
    }
    raw = {c['id']: {'html': c['html'], 'text': c['text']} for c in courses if c['raw']}
    LVK = {'初级': 'chu', '中级': 'zhong', '高级': 'gao', '专题': 'zhuan'}
    bodies = {k: {} for k in LVK.values()}
    for c in courses:
        if c['raw']:
            c['html'] = ''
            c['text'] = ''
        else:
            bodies[LVK[c['level']]][c['id']] = {'html': c['html'], 'text': c['text']}
            c['html'] = ''
            c['text'] = ''
    sizes = [
        ('data-raw.js', write_js('data-raw.js', 'DATA_RAW', raw)),
    ] + [('data-body-%s.js' % k, write_js('data-body-%s.js' % k, 'DATA_BODY_%s' % k, v)) for k, v in bodies.items()] + [
        ('data-course.js', write_js('data-course.js', 'DATA_COURSE', courses)),
        ('data-ref.js', write_js('data-ref.js', 'DATA_REF', ref)),
        ('data-qna.js', write_js('data-qna.js', 'DATA_QNA', qna)),
        ('data-st.js', write_js('data-st.js', 'DATA_ST', st)),
        ('data-notes.js', write_js('data-notes.js', 'DATA_NOTES', notes)),
        ('data-quiz.js', write_js('data-quiz.js', 'DATA_QUIZ', quiz)),
        ('data-meta.js', write_js('data-meta.js', 'DATA_META', meta)),
    ]
    print('== 构建完成 ==')
    for k, v in meta['counts'].items():
        print('  %-10s %s' % (k, v))
    for nme, sz in sizes:
        print('  %-16s %8.1f KB' % (nme, sz / 1024))
    for lv in meta['levels']:
        print('  ', lv)
    print('  topics', quiz['topics'])


if __name__ == '__main__':
    main()
