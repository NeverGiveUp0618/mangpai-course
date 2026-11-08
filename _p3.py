p='fixocr.py'; s=open(p).read()
s=s.replace("def fix_pan_line(l):","""DY_MAP = {'两': '丙', '王': '壬', '康': '庚', '日': '巳', '西': '酉', '成': '戌', '戍': '戌', '已': '巳', '末': '未', '卵': '卯', '展': '辰', '牛': '午', '玄': '亥'}


def fix_dayun(l):
    # 大运行：甲辰 乙日 两午 → 甲辰 乙巳 丙午（只在大运行内、「干+支」成对处订正）
    def pair(m):
        g, z = m.group(1), m.group(2)
        g = {'两': '丙', '王': '壬', '康': '庚'}.get(g, g)
        z = DY_MAP.get(z, z)
        return g + z
    return re.sub(r'([甲乙丙丁戊己庚辛壬癸两王康])([子丑寅卯辰巳午未申酉戌亥日西成戍已末卵展牛玄])(?![子丑寅卯辰巳午未申酉戌亥])', pair, l)


def fix_text(l):
    if '大运' in l[:6] or re.match(r'^[甲乙丙丁戊己庚辛壬癸两][子丑寅卯辰巳午未申酉戌亥日西成已末][ \\d（(]', l):
        l = fix_dayun(l)
    l = re.sub(r'([乙丁己辛癸])已', r'\\1巳', l)
    l = re.sub(r'已(?=[土])', '己', l)
    l = re.sub(r'已(?=[火申酉亥午未子丑寅卯辰戌合穿刑冲破])', '巳', l)
    l = re.sub(r'([甲庚壬丙])成(?![功就长为立])', r'\\1戌', l)
    l = re.sub(r'成(?=[土火中])', '戌', l)
    l = re.sub(r'([甲丙庚壬])戊(?![己癸土])', r'\\1戌', l)
    l = re.sub(r'两(?=[丁火午申寅辰子戌卯酉未亥])', '丙', l)
    l = re.sub(r'王(?=[申子辰午寅戌水癸亥])', '壬', l)
    l = l.replace('干文', '干支').replace('地文', '地支')
    return l


def fix_pan_line(l):""",1)
s=s.replace("        l = fix_pan_line(l)\n","        l = fix_pan_line(l)\n        l = fix_text(l)\n",1)
open(p,'w').write(s)
