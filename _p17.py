p='build_mp.py'; s=open(p).read()
old_start=s.index("        segs = [x for x in re.split(r'[，。；：、！？]', sums) if x]")
old_end=s.index("        brief = re.sub(r'^[乾坤][：:造]*', '', brief)")
new='''        GEN = re.compile(r'^(老师讲|分析|闲注|注|象|例|如|又如|此造|此人|该造|断|解|乾|坤|大运.*)$')
        segs = [re.sub(r'^(此造是|此造为|此人是|此人为|此造|此人|该造|本造)', '', x) for x in re.split(r'[，。；：、！？（）()]', sums) if x]
        segs = [x for x in segs if len(x) >= 5 and not GEN.match(x)]
        brief = segs[0] if segs else ''
        if len(brief) < 8 and len(segs) > 1:
            brief = brief + '，' + segs[1]
        brief = (brief[:20] or '命例')
'''
s=s[:old_start]+new+s[old_end:]
open(p,'w').write(s)
