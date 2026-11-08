p='convert.py'; s=open(p).read()
marker="    # —— 专题（小文档）——"
add='''    # —— 《盲派批命案例集》（263 例，早期口径：以用神为核心）——
    el = read_lines('S_案例集')
    GA = set(GAN) | set('已内两王康戍成巳戌')
    ZA = set(ZHI) | set('已卵末展牛玄西戍成戊己')
    hdr = [k for k, l in enumerate(el) if re.match(r'^例\\s*\\d+', l) and len(l) <= 40]
    early = []
    for j, k in enumerate(hdr):
        e = hdr[j + 1] if j + 1 < len(hdr) else len(el)
        blk = el[k:e]
        head = re.sub(r'^例\\s*\\d+', '', blk[0])
        rows = ([head] if head.strip(' ：:') else []) + blk[1:]
        sex = next((x for x in ('乾', '坤') if x in ' '.join(rows[:3])), '命')
        gi = zi = None
        for a, l in enumerate(rows[:8]):
            t = re.sub(r'^[^甲乙丙丁戊己庚辛壬癸已内两王康]*', '', l)
            t = re.sub(r'[\\s　]', '', t)
            if gi is None and len(t) >= 4 and all(c in GA for c in t[:4]) and sum(c in GAN for c in t[:4]) >= 2:
                gi = (a, t[:4]); continue
            if gi is not None and zi is None and not l.startswith('大运'):
                t2 = re.sub(r'[\\s　]', '', l)
                if len(t2) >= 4 and all(c in ZA for c in t2[:4]) and sum(c in ZHI for c in t2[:4]) >= 2:
                    zi = (a, t2[:4]); break
        if not (gi and zi):
            continue
        gan, zhi, stt = repair(gi[1], zi[1])
        if stt == 'ok':
            PROOF['ok'] += 1
        elif stt == 'fixed':
            PROOF['fixed'].append(('案例集 例%d' % (j + 1), gi[1] + '/' + zi[1], gan + '/' + zhi))
        else:
            PROOF['bad'].append(('案例集 例%d' % (j + 1), gi[1] + '/' + zi[1]))
        rest = [x for n, x in enumerate(rows) if n not in (gi[0], zi[0])]
        dy = [x for x in rest if x.startswith('大运')]
        body = [x for x in rest if not x.startswith('大运')]
        early.append({'sex': sex, 'gan': gan, 'zhi': zhi, 'body': '\\n'.join(body).strip(), 'sec': '案例集', 'chapter': '盲派批命案例集',
                      'book': '案例集（早期口径）', 'level': '专题', 'early': True, 'bad': stt == 'bad', 'dayun': ' '.join(dy)})
    allcases.extend(early)
    print('早期案例集命例：', len(early), '/ 例头', len(hdr))
    # 说明页（专题）：理论纲要部分
    intro = el[:hdr[0]] if hdr else []
    intro = [l for l in intro if not re.search(r'豆丁|docin|doc in|alpha|下载器|特别说明', l)]
    note = ['> ⚠️ **早期口径**：本资料成于段盲派理论成熟之前，仍以**用神、忌神、日主旺衰**为核心；与初、中、高级课程里「不论旺衰、不取用神」的成熟体系**口径不同**。收入仅作对照阅读，命例已在命例库标「早期口径」。', '',
            '> 【扫描件 OCR 转录，个别字词待校对】', ''] + [md_line(l) for l in intro]
    EARLY_NOTE = note

'''
s=s.replace(marker, add+marker,1)
# 专题末尾追加说明页
s=s.replace("    with io.open(os.path.join(ROOT, '_src', 'cases.json'), 'w', encoding='utf-8') as f:","""    write_doc('专题', seq, '案例集（早期口径）说明', EARLY_NOTE)
    stat.append(('专题', seq, '案例集（早期口径）说明', 0, 0, 0))
    with io.open(os.path.join(ROOT, '_src', 'cases.json'), 'w', encoding='utf-8') as f:""",1)
open(p,'w').write(s)
p='build_mp.py'; s=open(p).read()
s=s.replace("""        key = (c['sex'], gan, zhi)
        c['body'] = body
        if key not in best or len(body) > len(best[key]['body']):
            best[key] = c""","""        key = (c['sex'], gan, zhi)
        c['body'] = body
        old = best.get(key)
        if old is None or (old.get('early') and not c.get('early')) or \\
                (bool(old.get('early')) == bool(c.get('early')) and len(body) > len(old['body'])):
            best[key] = c""")
s=s.replace("TOPIC_ORDER = ['作用方式',","TOPIC_ORDER = ['作用方式',")
s=s.replace("'应期', '象法', '综合']","'应期', '象法', '综合', '早期案例（用神口径）']")
s=s.replace("def topic_of(c):\n","def topic_of(c):\n    if c.get('early'):\n        return '早期案例（用神口径）'\n")
s=s.replace("        tags = tags_of(sums)\n","        tags = tags_of(sums)\n        if c.get('early'):\n            tags = ['早期口径'] + tags\n            face = ('<p><span class=\"pill g\">⚠️ 早期口径：出自《盲派批命案例集》，仍以用神、旺衰为核心，与成熟体系不同，对照阅读</span></p>' +\n                    ('<p>' + c['dayun'] + '</p>' if c.get('dayun') else '')) + face\n",1)
open(p,'w').write(s)
