p='convert.py'; s=open(p).read()
s=s.replace("    jchunks = [('济南面授班教材·' + t, [OCRNOTE","    JT = ['应期', '象法', '财命专辑', '官命看法', '婚姻专辑', '学历专辑', '六亲（父母）']\n    jchunks = [(JT[k] if k < len(JT) else t, b) for k, (t, b) in enumerate(jchunks)]\n    jchunks = [('济南面授班教材·' + t, [OCRNOTE",1)
s=s.replace("ROOT = os.path.dirname(os.path.abspath(__file__))","ROOT = os.path.dirname(os.path.abspath(__file__))\nsys.path.insert(0, ROOT)\nfrom proof import repair, STAT as PROOF",1)
old="""            sex, gan, zhi, used, rest = p
            md.append('')
            md.append(pan_md(sex, gan, zhi))
            md.append('')
            cur = {'sex': sex, 'gan': gan, 'zhi': zhi, 'body': [], 'sec': sec}"""
new="""            sex, gan, zhi, used, rest = p
            og, oz = gan, zhi
            gan, zhi, stt = repair(gan, zhi)
            if stt == 'ok':
                PROOF['ok'] += 1
            elif stt == 'fixed':
                PROOF['fixed'].append((ctx, og + '/' + oz, gan + '/' + zhi))
            else:
                PROOF['bad'].append((ctx, og + '/' + oz))
            md.append('')
            md.append(pan_md(sex, gan, zhi))
            if stt == 'bad':
                md.append('')
                md.append('> ⚠️ 此盘干支组合不合历法（疑识别或原稿笔误），待对照原件校对。')
            md.append('')
            cur = {'sex': sex, 'gan': gan, 'zhi': zhi, 'body': [], 'sec': sec, 'bad': stt == 'bad'}"""
assert old in s
s=s.replace(old,new,1)
old2="    print('cases raw:', len(allcases))"
new2="""    print('cases raw:', len(allcases))
    with io.open(os.path.join(ROOT, '_src', 'proof_report.txt'), 'w', encoding='utf-8') as f:
        f.write('盘面校验：通过 %d，自动订正 %d，存疑 %d\\n\\n[自动订正]\\n' % (PROOF['ok'], len(PROOF['fixed']), len(PROOF['bad'])))
        for c, a, b in PROOF['fixed']:
            f.write('%s  %s → %s\\n' % (c, a, b))
        f.write('\\n[存疑]\\n')
        for c, a in PROOF['bad']:
            f.write('%s  %s\\n' % (c, a))
    print('校验：通过', PROOF['ok'], '订正', len(PROOF['fixed']), '存疑', len(PROOF['bad']))"""
assert old2 in s
s=s.replace(old2,new2,1)
open(p,'w').write(s)
