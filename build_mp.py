#!/usr/bin/env python3
"""content/**.md + _src/cases.json → data/*.js（与 bazi-course 同构的数据包）。

流程：python3 convert.py（原始文本→md/cases）→ python3 build_mp.py（md→data）。
data/*.js 全是产物，别手改。
"""
import os, re, io, json, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from mdlite import md2html, strip_md, render_chart  # noqa

CONTENT = os.path.join(ROOT, 'content')
OUT = os.path.join(ROOT, 'data')
LEVELS = ['初级', '中级', '高级']

GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
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


def write_js(name, var, obj):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    with io.open(p, 'w', encoding='utf-8') as f:
        f.write('window.%s=%s;\n' % (var, json.dumps(obj, ensure_ascii=False, separators=(',', ':'))))
    return os.path.getsize(p)


def read(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read()


def build_doc(path, ident, n, title, extra):
    s = read(path)
    s = re.sub(r'^#\s+.*?\n', '', s, count=1)
    heads = []
    html = md2html(s, heading_offset=0, collect_headings=heads, manual=False)
    d = {
        'id': ident, 'n': n, 'title': title, 'html': html,
        'toc': [{'lv': lv, 't': t, 'a': a, 'st': 0, 'm': 0} for lv, t, a in heads if lv <= 3],
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


def build_courses():
    books = json.load(io.open(os.path.join(ROOT, '_src', 'books.json'), encoding='utf-8'))
    bymap = {(b['level'], b['n']): b['book'] for b in books}
    docs, n = [], 1

    def add(path, title, lv, book, raw):
        nonlocal n
        docs.append(build_doc(path, 'c%d' % n, n, title, {'level': lv, 'book': book, 'raw': raw}))
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
        # 原稿（逐字整理）
        d = os.path.join(CONTENT, lv)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                m = re.match(r'^(\d+)-(.+)\.md$', fn)
                if m:
                    add(os.path.join(d, fn), first_title(os.path.join(d, fn), m.group(2)), lv,
                        bymap.get((lv, int(m.group(1))), ''), True)
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

TOPIC_RULES = [
    ('正局反局', r'正局|反局'), ('财运', r'财命|财富|取财|求财|财运'), ('官运', r'官命|官运|官贵|当官|军官'),
    ('婚姻', r'婚|夫妻|独身|离婚|桃花|淫乱|配偶'), ('六亲', r'父母|六亲|子女|看寿|兄弟'),
    ('学历', r'学历'), ('牢狱', r'牢狱|犯罪'), ('疾病', r'疾病|病'), ('职业', r'职业|医生|老师|会计|口才|军官|盲人'),
    ('应期', r'应期|大运'), ('象法', r'象|类象'), ('作用方式', r'合|冲|穿|刑|破|墓|制|做功|体用|宾主|虚实|互通'),
]
TOPIC_ORDER = ['作用方式', '正局反局', '财运', '官运', '职业', '婚姻', '六亲', '学历', '牢狱', '疾病', '应期', '象法', '综合', '早期案例（用神口径）']


def topic_of(c):
    if c.get('early'):
        return '早期案例（用神口径）'
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
    md = '\n\n'.join(l.strip() for l in text.split('\n') if l.strip())
    return md2html(md, heading_offset=0)


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
        m = MARK.search(body)
        pre = body[:m.start()].strip() if m else ''
        jie = body[m.start():] if m else body
        jie = re.sub(r'^(简历及解析|简历及简析|解析|分析|解)[：:]', '', jie).strip()
        sums = re.sub(r'[\s　]+', '', jie)
        GEN = re.compile(r'^(老师讲|分析|闲注|注|象|例|如|又如|此造|此人|该造|断|解|乾|坤|大运.*)$')
        sums2 = re.sub(r'(闲注|分析|断|解|注)[:：]', '，', sums)
        segs = [re.sub(r'^(此造是|此造为|此人是|此人为|此造|此人|该造|本造)', '', x) for x in re.split(r'[，。；：:、！？（）()\.\s]', sums2) if x]
        segs = [x for x in segs if sum(c in GAN + ZHI for c in x) <= len(x) * 0.4]
        segs = [x for x in segs if len(x) >= 5 and not GEN.match(x)]
        brief = segs[0] if segs else ''
        if len(brief) < 8 and len(segs) > 1:
            brief = brief + '，' + segs[1]
        brief = (brief[:20] or '命例')
        brief = re.sub(r'^[乾坤][：:造]*', '', brief)
        title = '%s造 %s%s日 · %s' % (sex, day, zhi[2], brief)
        ss_g = ' '.join('%s%s' % (p, shishen(day, g)) for p, g in zip('年月时', [gan[0], gan[1], gan[3]]))
        ss_z = ' '.join('%s%s' % (p, shishen(day, BEN[z])) for p, z in zip('年月日时', zhi))
        chai = ('<p><strong>%s日主</strong></p>' % day) + render_chart(gan, zhi, sex) + \
               '<p><strong>天干十神</strong>：%s</p><p><strong>地支（取本气）</strong>：%s</p>' % (ss_g, ss_z)
        face = ''
        if pre:
            face += para_html(pre)
        face += ('<p>先别看解：这个盘<strong>日主%s</strong>，想一想——<strong>谁和谁做功？用的是什么作用方式？</strong>'
                 '大运怎么走？推完再点「解」对照。</p>') % day
        tags = tags_of(sums)
        if c.get('early'):
            tags = ['早期口径'] + tags
            face = ('<p><span class="pill g">⚠️ 早期口径：出自《盲派批命案例集》，仍以用神、旺衰为核心，与成熟体系不同，对照阅读</span></p>' +
                    ('<p>' + c['dayun'] + '</p>' if c.get('dayun') else '')) + face
        if c.get('bad'):
            tags = ['待校对'] + tags
            face += '<p><span class="pill g">⚠️ 此盘干支组合不合历法，疑识别或原稿笔误，待对照原件校对</span></p>'
        for t in tags:
            tagcount[t] = tagcount.get(t, 0) + 1
        topic = topic_of(c)
        items.append({
            'n': 0, 'title': title, 'tags': tags, 'star': 0,
            'chart': {'g': sex, 'gan': gan, 'zhi': zhi}, 'nCharts': 1,
            'charts': [{'g': sex, 'gan': gan, 'zhi': zhi, 'label': ''}],
            'face': face, 'jieLabel': '解', 'jie': para_html(jie), 'chai': chai, 'noAnswer': 0,
            'text': sums[:4000], 'topic': topic, 'seq': 0,
            '_src': '%s · %s' % (c.get('book', ''), c.get('chapter', '')),
        })
    # 按主题顺序排，再给连续号
    items.sort(key=lambda x: (TOPIC_ORDER.index(x['topic']), x['_src']))
    for i, it in enumerate(items, 1):
        it['n'] = i
        it['seq'] = i
        it['jie'] += '<p class="src-line"><span class="src">出处：%s</span></p>' % it.pop('_src')
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
    ('体系总览与宫位', ['盲派体系总览', '宫位取象'], ['天道、阴阳', '十神与宫位', '宫位类象'], ['体用宾主']),
    ('十神与类象', ['十神类象'], ['干支类象', '宫位类象与十神'], ['宫位、十神、神煞类象深化', '干支象义']),
    ('干支与虚实', ['十天干', '干支配置'], ['十天干象义', '干支关系', '十二地支象义', '干支虚实'], []),
    ('合', ['合（一）', '合（二）', '合（三）'], ['地支作用'], ['天干五合与地支六合']),
    ('冲、穿、刑、破、墓', ['刑、破、害、墓', '冲、穿（一）', '冲、穿（二）'], [], ['三合、六冲']),
    ('做功与效率', ['做功方式'], ['象的应用'], ['能量效率']),
    ('正局与反局', ['基础问题'], ['正局与反局'], ['正局反局进阶']),
    ('入手与层次', ['入手方法'], [], []),
    ('大运流年与应期', ['应期入门'], ['应期'], ['大运流年与应期']),
    ('财与官', [], ['财命专辑', '官命看法'], ['财命的高级断法', '官命、职业与学历']),
    ('婚姻', ['婚姻与看寿'], ['婚姻专辑'], ['婚姻宫', '恋爱同居', '男命多婚', '女命多婚', '婚外情', '包局婚姻', '配偶情况', '伤克配偶', '独身组合', '差婚姻']),
    ('六亲（父母）', [], [], ['父母死亡', '父母离异']),
    ('学历、牢狱与实战', [], ['学历与牢狱', '实战演示'], []),
    ('职业象法', [], [], ['职业象法']),
]


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
    h.append('<h2 id="顺序">建议顺序</h2><ol><li><strong>初级</strong>：按章顺序通读（18 章），重点是体系总览、宫位、十神、干支配置、合冲穿刑破墓、做功方式。</li>'
             '<li><strong>中级</strong>：先读「干支奥义」七章打牢象义，再读正局反局、应期、类象与象的应用，最后读财官婚学牢专辑。</li>'
             '<li><strong>高级</strong>：先读作用方式深论、体用宾主与能量效率，再按需要读婚姻六亲与职业象法。</li></ol>')
    return ''.join(h)


def main():
    courses = build_courses()
    notes = build_notes()
    quiz = build_quiz()
    meta = {
        'name': '盲派八字', 'built': time.strftime('%Y-%m-%d %H:%M'),
        'counts': {'course': sum(1 for c in courses if not c['raw']) or len(courses), 'rawCourse': sum(1 for c in courses if c['raw']), 'notes': len(notes), 'quiz': len(quiz['items']),
                   'quizChart': len(quiz['items']), 'quizChai': len(quiz['items'])},
        'levels': [{'name': lv, 'n': sum(1 for c in courses if c['level'] == lv and not c['raw']), 'raw': sum(1 for c in courses if c['level'] == lv and c['raw'])} for lv in LEVELS],
        'outline': build_outline(courses, notes, quiz),
    }
    raw = {c['id']: {'html': c['html'], 'text': c['text']} for c in courses if c['raw']}
    for c in courses:
        if c['raw']:
            c['html'] = ''
            c['text'] = ''
    sizes = [
        ('data-raw.js', write_js('data-raw.js', 'DATA_RAW', raw)),
        ('data-course.js', write_js('data-course.js', 'DATA_COURSE', courses)),
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
