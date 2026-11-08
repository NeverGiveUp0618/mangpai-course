#!/usr/bin/env python3
"""把 _src/txt 里的原始资料转成 content/**.md（课程）与 _src/cases.json（命例）。

只收「成熟期」资料（2006–2011）。早期用神口径（命理珍宝/授课教程/263例）与
扫描 PDF（OCR 错字多）不收，见 README。
内容源 = _src/txt（不进 git）；产物 content/*.md 是 build_mp.py 的输入。
"""
import os, re, json, io, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(ROOT, '_src', 'txt')
OUT = os.path.join(ROOT, 'content')

GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
NOISE = re.compile(r'HYPERLINK|PAGEREF|INCLUDEPICTURE|MERGEFORMAT|TOC \\o|\[replyview\]|bolead\.com')
NUMZH = '一二三四五六七八九十'
# 本站不收奇门／六爻等无关术数的段落（原资料里只是拿来类比的几句）
OFFTOPIC = re.compile(r'六爻|奇门|梅花易|八字卦')

# ── 排盘识别 ─────────────────────────────────────────────
G4 = r'((?:[%s][\s　]*){4})' % GAN
Z4 = r'((?:[%s][\s　]*){4})' % ZHI
# 乾造：甲甲丙壬 \n 申戌寅辰   或   乾造：甲甲丙壬 申戌寅辰   或 乾：辛　丙　己　甲\n    亥　申　丑　戌
PAN2 = re.compile(r'(乾|坤)\s*造?\s*[：:，,]?\s*' + G4 + r'[\s　]*\n?[\s　]*' + Z4)
PAN_ONE = re.compile(r'(乾|坤)\s*造?\s*[：:，,]?\s*' + G4 + r'[\s　]+' + Z4)


def squash(s):
    return re.sub(r'[\s　]+', '', s)


def clean_lines(text):
    out = []
    for l in text.replace('\r', '').split('\n'):
        l = l.replace('\ue004', '').replace('\u200b', '').strip()
        l = re.sub(r'[ \t　]+', ' ', l) if not re.match(r'^[甲乙丙丁戊己庚辛壬癸]', l) else l
        if not l or NOISE.search(l) or OFFTOPIC.search(l):
            continue
        out.append(l)
    return out


def find_pan(lines, i):
    """从 lines[i] 起识别排盘（可能跨两行）。返回 (sex, gan, zhi, 用掉的行数, 行尾剩余文字) 或 None。"""
    a = lines[i]
    nxt = lines[i + 1] if i + 1 < len(lines) else ''
    # 同行 gan zhi
    m = re.match(r'^(乾|坤)\s*造?\s*[：:，,]?\s*' + G4 + r'[\s　]+' + Z4 + r'(.*)$', a)
    if m:
        return m.group(1), squash(m.group(2)), squash(m.group(3)), 1, m.group(4).strip()
    m = re.match(r'^[●•·\s]*(乾|坤)\s*造?\s*[：:，,]?\s*' + G4 + r'[（(][^）)]{0,12}[）)]\s*(.*)$', a)
    if m:
        n = re.match(r'^' + Z4 + r'(.*)$', nxt)
        if n:
            return m.group(1), squash(m.group(2)), squash(n.group(1)), 2, ((m.group(3) or '') + ' ' + (n.group(2) or '')).strip()
    m = re.match(r'^(乾|坤)\s*造?\s*[：:，,]?\s*' + G4 + r'(.*)$', a)
    if m:
        rest = m.group(3).strip()
        # 大运可能紧跟在干行后：「大运：」
        n = re.match(r'^' + Z4 + r'(.*)$', nxt)
        if n and not rest.startswith('大运') or (n and rest == ''):
            return m.group(1), squash(m.group(2)), squash(n.group(1)), 2, (n.group(2) or '').strip()
        n = re.match(r'^' + Z4 + r'(.*)$', nxt)
        if n:
            return m.group(1), squash(m.group(2)), squash(n.group(1)), 2, ((rest + ' ' + (n.group(2) or '')).strip())
    return None


def pan_md(sex, gan, zhi):
    return '**%s造**：%s／%s' % (sex, gan, zhi)


# ── 标题识别 ─────────────────────────────────────────────
H_CH = re.compile(r'^第[%s百]+章[、．. \s]*(.*)$' % NUMZH)
H_SEC = re.compile(r'^第[%s]+节[：:、．. \s]*(.*)$' % NUMZH)
H_NUM = re.compile(r'^[%s]{1,3}[、．.]\s*(.{2,28})$' % NUMZH)
H_PAR = re.compile(r'^[（(][%s]{1,3}[）)]\s*(.{2,28})$' % NUMZH)
H_BRACKET = re.compile(r'^【(.{2,16})】[：:]?$')
PUNCT = re.compile(r'[，。；？！]')


def is_short_head(s):
    return len(s) <= 30 and not PUNCT.search(s) and '…' not in s


SPEAKER = re.compile(r'^(问|答|卜文|言明|博文|梅子|闲注|注|分析|学员|段师|老师|小月狐|闲)[：:]')


def md_line(l):
    l = l.strip()
    m = SPEAKER.match(l)
    if m:
        k = m.group(1)
        return '**%s**：%s' % (k, l[m.end():].strip())
    return l


def convert_chunk(lines, h2, h3, h4=None, cases=None, ctx=''):
    """lines → markdown 行；顺手把命例收进 cases。h2/h3/h4: 判定函数 line→标题文本或 None。"""
    md = []
    i = 0
    cur = None          # 正在收集的命例
    sec = ctx
    def flush():
        nonlocal cur
        if cur is not None and cases is not None:
            body = '\n'.join(cur['body']).strip()
            cur['body'] = body
            cases.append(cur)
        cur = None
    while i < len(lines):
        l = lines[i]
        p = find_pan(lines, i)
        if p:
            flush()
            sex, gan, zhi, used, rest = p
            md.append('')
            md.append(pan_md(sex, gan, zhi))
            md.append('')
            cur = {'sex': sex, 'gan': gan, 'zhi': zhi, 'body': [], 'sec': sec}
            if rest:
                md.append(md_line(rest)); cur['body'].append(rest)
            i += used
            continue
        t2 = h2(l) if h2 else None
        t3 = h3(l) if h3 else None
        t4 = h4(l) if h4 else None
        if t2 or t3 or t4:
            flush()
            if t2:
                md.append(''); md.append('## ' + t2); md.append(''); sec = t2
            elif t3:
                md.append(''); md.append('### ' + t3); md.append(''); sec = t3 if not sec else sec
            else:
                md.append(''); md.append('#### ' + t4); md.append('')
            i += 1
            continue
        md.append(md_line(l)); md.append('')
        if cur is not None:
            cur['body'].append(l)
        i += 1
    flush()
    # 压缩多余空行
    out = []
    for x in md:
        if x == '' and out and out[-1] == '':
            continue
        out.append(x)
    return out


def sub_head(l, pat):
    l2 = l.rstrip('。：:； ')
    m = pat.match(l2)
    if m and is_short_head(l2):
        return l2
    return None


def make_h2(kind):
    def f(l):
        if kind == 'ch':     # 第X节
            m = H_SEC.match(l)
            return (l if m and is_short_head(l) else None)
        if kind == 'num':    # 一、xxx
            return sub_head(l, H_NUM)
        return None
    return f


PAN_ANY = re.compile(r'(?:(乾|坤)\s*造?|例)\s*[：:，,]?\s*((?:[%s][\s　]*){4})\s*((?:[%s][\s　]*){4})' % (GAN, ZHI))
SPK = re.compile(r'(?<=[。！？\s）)])(问|答|卜文|言明|博文|学员|梅子|小月狐)[：:]')


def presplit(text):
    text = text.replace('★', '\n★')
    def fix(m):
        sex = m.group(1) or '乾'
        return '\n%s造：%s %s ' % (sex, squash(m.group(2)), squash(m.group(3)))
    text = PAN_ANY.sub(fix, text)
    text = SPK.sub(lambda m: '\n' + m.group(0), text)
    text = re.sub(r'(分析[：:]|断[：:]|注[：:])', lambda m: '\n' + m.group(0), text)
    return text


def read_lines(name, pre=False):
    if pre:
        return clean_lines(presplit(io.open(os.path.join(TXT, name + '.txt'), encoding='utf-8').read()))
    return clean_lines(io.open(os.path.join(TXT, name + '.txt'), encoding='utf-8').read())


def split_chunks(lines, pat, min_body=150, title_fn=None):
    """按章标题切块，丢掉目录里那种几乎没正文的块。返回 [(title, lines)]。"""
    idx = []
    for i, l in enumerate(lines):
        m = pat.match(l)
        if m and len(l) <= 40 and not PUNCT.search(l) and '…' not in l:
            idx.append((i, re.sub(r'\s+', '', title_fn(l, m) if title_fn else l)))
    # 目录里的同名标题：只留最后一轮
    if idx:
        first = idx[0][1]
        last_first = max(k for k, (_, t) in enumerate(idx) if t == first)
        idx = idx[last_first:]
    chunks = []
    for k, (i, t) in enumerate(idx):
        j = idx[k + 1][0] if k + 1 < len(idx) else len(lines)
        body = lines[i + 1:j]
        if sum(len(x) for x in body) >= min_body:
            chunks.append((t, body))
    return chunks


def chn(l, m):
    t = re.sub(r'^第[%s百]+章[、．. \s]*' % NUMZH, '', l).strip()
    return t or l


# ── 各册配置 ─────────────────────────────────────────────
BOOKS = []
BOOKMAP = []


def write_doc(level, seq, title, md_lines):
    d = os.path.join(OUT, level)
    os.makedirs(d, exist_ok=True)
    fn = os.path.join(d, '%02d-%s.md' % (seq, re.sub(r'[\\/:*?"<>|]', '', title)[:40]))
    with io.open(fn, 'w', encoding='utf-8') as f:
        f.write('# ' + title + '\n\n' + '\n'.join(md_lines).strip() + '\n')
    return fn


def run():
    for lv in ('初级', '中级', '高级', '专题'):
        d = os.path.join(OUT, lv)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith('.md'):
                    os.remove(os.path.join(d, f))
    allcases = []
    stat = []
    global BOOKMAP
    BOOKMAP = []

    counters = {}

    def emit(level, label, chunks, h2=None, h3=None, prefix=''):
        n = counters.get(level, 1)
        for t, body in chunks:
            cases = []
            md = convert_chunk(body, h2, h3, None, cases, ctx=t)
            title = (prefix + t).strip()
            fn = write_doc(level, n, title, md)
            for c in cases:
                c['book'] = label; c['level'] = level; c['chapter'] = t
            allcases.extend(cases)
            stat.append((level, n, title, sum(len(x) for x in md), len(cases)))
            BOOKMAP.append({'level': level, 'n': n, 'book': label, 'title': title})
            n += 1
        counters[level] = n

    def group_book(level, label, lines, pat, prefix, target=14000):
        chunks = split_chunks(lines, pat, min_body=60, title_fn=lambda l, m: l)
        groups, cur, size = [], [], 0
        for t, body in chunks:
            cur.append((t, body)); size += sum(len(x) for x in body)
            if size >= target:
                groups.append(cur); cur = []; size = 0
        if cur:
            if groups and size < target / 3:
                groups[-1].extend(cur)
            else:
                groups.append(cur)
        out = []
        for k, g in enumerate(groups, 1):
            ls = []
            for t, body in g:
                ls.append('§§' + t); ls.extend(body)
            out.append((prefix if len(groups) == 1 else '%s·第%s部分' % (prefix, NUMZH[k - 1]), ls))
        h2x = lambda l: (l[2:] if l.startswith('§§') else None)
        emit(level, label, out, h2x, None, '')

    def book(level, label, src, pat, h2=None, h3=None, prefix='', tf=chn, min_body=150, lines=None):
        ls = lines if lines is not None else read_lines(src)
        emit(level, label, split_chunks(ls, pat, min_body=min_body, title_fn=tf), h2, h3, prefix)

    H_NUM2 = lambda l: sub_head(l, H_NUM)
    H_SEC2 = lambda l: sub_head(l, H_SEC)

    # —— 初级 ——
    book('初级', '网授班辅导资料', '盲派命理网授班辅导资料', H_CH, H_SEC2, H_NUM2)
    book('初级', '初级班整理版', '盲派初级命理（整理版）', H_CH, H_SEC2, H_NUM2)
    dl = read_lines('大连段建业-面授讲义（合集）134页')
    def find(prefix, start=0):
        for k in range(start, len(dl)):
            if dl[k].startswith(prefix):
                return k
        return None
    iJN = find('济南面授笔记'); iB = find('一、如何看八字（看八字的玄机）', iJN or 0); iYC = find('盐城面授笔记', iB or 0)
    print('大连分段点', iJN, iB, iYC)
    book('初级', '大连面授讲义', None, H_BRACKET, H_NUM2, None, tf=lambda l, m: m.group(1), min_body=300, lines=dl[:iJN])
    # —— 中级 ——
    book('中级', '中级班讲义', '盲师中级（整理版）--广州+太原笔记', H_CH, H_SEC2, H_NUM2)
    # —— 高级 ——
    book('高级', '高级班讲义', '盲师命理高级班讲义a', H_CH, H_SEC2, H_NUM2, prefix='高级班·')
    NUMCH = re.compile(r'^[%s]{1,3}[、．.]\s*(.{2,28})$' % NUMZH)
    group_book('高级', '济南面授笔记', dl[iJN:iB], NUMCH, '济南面授笔记')
    group_book('高级', '面授笔记（二）', dl[iB:iYC], NUMCH, '另一场面授笔记')
    DAYS = re.compile(r'^(五月[一二三四五六七八九十]+[日号]?[上下晚]午?晚?上?笔记)$')
    group_book('高级', '盐城面授笔记', dl[iYC:], DAYS, '盐城面授笔记', target=30000)
    ql = read_lines('段建业2011武当山六亲班高级面授讲课笔记')
    qch = [('婚姻专辑', 0), ('父母', 0)]
    cut = None
    for k, l in enumerate(ql):
        if re.match(r'^第二章[：:\s]*父母', l) and '…' not in l:
            cut = k
    first_start = next((k for k, l in enumerate(ql) if re.match(r'^第一章\s*婚姻专辑$', l)), 0)
    SEC1 = re.compile(r'^第[%s]+节[：:、．.\s]*(.*)$' % NUMZH)
    tf_sec = lambda l, m: re.sub(r'^第[%s]+节[：:、．.\s]*' % NUMZH, '', l)
    book('高级', '武当山六亲班', None, SEC1, None, H_NUM2, prefix='六亲班·婚姻·', tf=tf_sec, min_body=200, lines=ql[first_start:cut])
    book('高级', '武当山六亲班', None, SEC1, None, H_NUM2, prefix='六亲班·父母·', tf=tf_sec, min_body=200, lines=ql[cut:])

    # —— 专题（小文档）——
    SMALL = [
        ('体用', '体用'), ('宾主作用', '宾主作用'), ('应期', '应期'), ('墓  穿', '墓与穿'),
        ('伤官', '伤官'), ('六亲', '六亲'), ('命格组合', '命格组合'), ('象法', '象法'),
        ('象的应用', '象的应用'), ('口才求财', '口才与求财'), ('会计 医生 老师', '会计、医生、老师'),
        ('如何看军官', '如何看军官'), ('疾病', '疾病'), ('婚姻专辑', '婚姻专辑（问答）'),
        ('肓派断命记录', '断命记录'), ('辅导站中答疑汇编', '辅导站答疑汇编'), ('盲师断命秘录', '命术轶闻（夏仲奇断例）'),
    ]
    BAN = re.compile(r'六爻|奇门|梅花|八字卦|大六壬|六壬')
    seq = 1
    for src, title in SMALL:
        lines = read_lines(src, pre=True)
        # ★ 分条，丢掉与本站无关的条目
        items, curi = [], []
        for l in lines:
            if l.startswith('★') and curi:
                items.append(curi); curi = []
            curi.append(l)
        if curi:
            items.append(curi)
        keep, dropped = [], 0
        for it in items:
            if BAN.search(' '.join(it)):
                dropped += 1
                it = [x for x in it if not BAN.search(x)]
                if sum(len(x) for x in it) < 400:
                    continue
            keep.append(it)
        flat = []
        for it in keep:
            first = it[0]
            if first.startswith('★'):
                flat.append('★§' + first[1:].strip())   # 占位，下面换成小标题
                flat.extend(it[1:])
            else:
                flat.extend(it)
        cases = []
        md = convert_chunk(flat, lambda l: (l[2:] if l.startswith('★§') and len(l) < 60 else None), None, None, cases, ctx=title)
        # 长 ★ 行：转为加粗段
        md = [('**' + x[2:].strip() + '**') if x.startswith('★§') else x for x in md]
        write_doc('专题', seq, title, md)
        for c in cases:
            c['book'] = '专题'; c['level'] = '专题'; c['chapter'] = title
        allcases.extend(cases)
        stat.append(('专题', seq, title, sum(len(x) for x in md), len(cases), dropped))
        seq += 1

    with io.open(os.path.join(ROOT, '_src', 'cases.json'), 'w', encoding='utf-8') as f:
        json.dump(allcases, f, ensure_ascii=False)
    with io.open(os.path.join(ROOT, '_src', 'books.json'), 'w', encoding='utf-8') as f:
        json.dump(BOOKMAP, f, ensure_ascii=False)
    for s in stat:
        print(s)
    print('cases raw:', len(allcases))


if __name__ == '__main__':
    run()
