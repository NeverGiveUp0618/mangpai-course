import re
# ---- build_mp.py：教材 + 原稿 ----
p = 'build_mp.py'
s = open(p).read()
a = s.index('def build_courses():')
b = s.index('def build_notes():')
new = '''def build_courses():
    books = json.load(io.open(os.path.join(ROOT, '_src', 'books.json'), encoding='utf-8'))
    bymap = {(b['level'], b['n']): b['book'] for b in books}
    docs, n = [], 1

    def add(path, title, lv, book, raw):
        nonlocal n
        docs.append(build_doc(path, 'c%d' % n, n, title, {'level': lv, 'book': book, 'raw': raw}))
        n += 1

    def first_title(path, fallback):
        return read(path).split('\\n', 1)[0].lstrip('# ').strip() or fallback

    for lv in LEVELS:
        # 教材（改写稿）
        d = os.path.join(CONTENT, '教材', lv)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                m = re.match(r'^(\\d+)-(.+)\\.md$', fn)
                if m:
                    add(os.path.join(d, fn), first_title(os.path.join(d, fn), m.group(2)), lv, '教材', False)
        # 原稿（逐字整理）
        d = os.path.join(CONTENT, lv)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                m = re.match(r'^(\\d+)-(.+)\\.md$', fn)
                if m:
                    add(os.path.join(d, fn), first_title(os.path.join(d, fn), m.group(2)), lv,
                        bymap.get((lv, int(m.group(1))), ''), True)
    return docs


'''
s = s[:a] + new + s[b:]
s = s.replace("'counts': {'course': len(courses),", "'counts': {'course': sum(1 for c in courses if not c['raw']) or len(courses), 'rawCourse': sum(1 for c in courses if c['raw']),")
s = s.replace("'levels': [{'name': lv, 'n': sum(1 for c in courses if c['level'] == lv)} for lv in LEVELS],",
              "'levels': [{'name': lv, 'n': sum(1 for c in courses if c['level'] == lv and not c['raw']), 'raw': sum(1 for c in courses if c['level'] == lv and c['raw'])} for lv in LEVELS],")
s = s.replace("        cs = [c for c in courses if c['level'] == lv]\n", "        cs = [c for c in courses if c['level'] == lv and not c['raw']]\n")
open(p, 'w').write(s)

# ---- style.css：新配色 + 盘 ----
p = 'style.css'
s = open(p).read()
s = s.replace('/* 盲派八字 — 宣纸赭墨 */', '/* 盲派八字 — 松烟墨绿 */')
# light
s = s.replace('--bg:#f2ede0; --bg2:#e8e1d0; --card:#fdfbf5; --line:#ddd4c0;', '--bg:#f3f1ea; --bg2:#e8e5da; --card:#fbfaf6; --line:#d8d4c4;')
s = s.replace('--ink:#2b2b28; --ink2:#5c5850; --ink3:#8b857a;', '--ink:#232826; --ink2:#55605b; --ink3:#87908b;')
s = s.replace('--indigo:#7a3b22; --indigo2:#a0522d; --indigo-soft:#f1e4da;', '--indigo:#2d5a4b; --indigo2:#3f7b67; --indigo-soft:#e1ece6;')
# dark
s = s.replace('--bg:#16191c; --bg2:#1b1f23; --card:#212629; --line:#333a3f;', '--bg:#111614; --bg2:#161c19; --card:#1b2220; --line:#2c3632;')
s = s.replace('--ink:#dfe3e6; --ink2:#a8b0b6; --ink3:#79838a;', '--ink:#e2e8e4; --ink2:#a8b4ad; --ink3:#78867f;')
s = s.replace('--indigo:#e0976c; --indigo2:#eeb08a; --indigo-soft:#33231b;', '--indigo:#7fc3a8; --indigo2:#9bd4bd; --indigo-soft:#1a2b25;')
# 五行色（亮）
s = s.replace('--wx-mu:#2e7d5b;    /* 木 · 青 */', '--wx-mu:#3f8a2f;    /* 木 · 青 */')
s = s.replace('--wx-huo:#c0392b;   /* 火 · 赤 */', '--wx-huo:#d6452a;   /* 火 · 赤 */')
s = s.replace('--wx-tu:#7a4a24;    /* 土 · 棕 */', '--wx-tu:#8c5a2b;    /* 土 · 棕 */')
s = s.replace('--wx-jin:#a06d1f;   /* 金 · 金黄 */', '--wx-jin:#b88a10;   /* 金 · 金黄 */')
s = s.replace('--wx-shui:#1f4e79;  /* 水 · 玄 */', '--wx-shui:#2a5f9e;  /* 水 · 玄 */')
s = s.replace('--wx-mu:#5fbf8f; --wx-huo:#e8705f; --wx-tu:#b07d54;', '--wx-mu:#7bd16a; --wx-huo:#ff7a5c; --wx-tu:#d19a62;')
s = s.replace('--wx-jin:#d9a94e; --wx-shui:#6fa8dc;', '--wx-jin:#f0c24b; --wx-shui:#78b4ee;')
s = s.replace('--wx-mu:#2e7d5b; --wx-huo:#c0392b; --wx-tu:#7a4a24;', '--wx-mu:#3f8a2f; --wx-huo:#d6452a; --wx-tu:#8c5a2b;')
s = s.replace('--wx-jin:#a06d1f; --wx-shui:#1f4e79;', '--wx-jin:#b88a10; --wx-shui:#2a5f9e;')
s = s.replace('linear-gradient(140deg,var(--indigo) 0%, #5a2b19 60%, #3b1c10 100%)', 'linear-gradient(140deg,var(--indigo) 0%, #1f4237 60%, #14302a 100%)')
# 四柱盘：每个字一枚五行色牌（正文吸顶盘 + 命例吸顶盘 + 题内盘）
s += '''
/* ===== 四柱盘重设计：五行色牌 ===== */
.doc .ichart .c .a,.doc .ichart .c .b,.sticky-chart .c .a,.sticky-chart .c .b{
  display:block; margin:2px auto 0; width:30px; line-height:30px; height:30px; border-radius:8px;
  text-align:center; font-size:18px; font-weight:700; background:var(--bg2); box-shadow:inset 0 0 0 1px var(--line);
}
.doc .ichart .c .a.w-mu,.doc .ichart .c .b.w-mu,.sticky-chart .c .w-mu{background:color-mix(in srgb,var(--wx-mu) 16%,transparent); box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--wx-mu) 45%,transparent)}
.doc .ichart .c .a.w-huo,.doc .ichart .c .b.w-huo,.sticky-chart .c .w-huo{background:color-mix(in srgb,var(--wx-huo) 16%,transparent); box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--wx-huo) 45%,transparent)}
.doc .ichart .c .a.w-tu,.doc .ichart .c .b.w-tu,.sticky-chart .c .w-tu{background:color-mix(in srgb,var(--wx-tu) 16%,transparent); box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--wx-tu) 45%,transparent)}
.doc .ichart .c .a.w-jin,.doc .ichart .c .b.w-jin,.sticky-chart .c .w-jin{background:color-mix(in srgb,var(--wx-jin) 18%,transparent); box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--wx-jin) 50%,transparent)}
.doc .ichart .c .a.w-shui,.doc .ichart .c .b.w-shui,.sticky-chart .c .w-shui{background:color-mix(in srgb,var(--wx-shui) 16%,transparent); box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--wx-shui) 45%,transparent)}
.doc .ichart .c.day,.sticky-chart .c.day{background:none; box-shadow:none; border-radius:10px; outline:2px solid var(--indigo2); outline-offset:1px}
.doc .ichart,.sticky-chart{box-shadow:0 4px 12px rgba(0,0,0,.08)}
/* 课程列表：级别折叠组 */
.lvg{background:var(--card); border:1px solid var(--line); border-radius:14px; margin:0 0 12px; overflow:hidden}
.lvg>.qgh .nm{font-size:16.5px; letter-spacing:.06em}
.lvg>.qgb{padding:4px 12px 12px}
.lvg .card{margin:8px 0 0; box-shadow:none}
.rawg{margin-top:12px; border-top:1px dashed var(--line); border-bottom:0}
'''
open(p, 'w').write(s)
print('ok')
