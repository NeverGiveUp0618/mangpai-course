#!/usr/bin/env python3
"""把 Vision OCR 出来的 V_*.txt（按物理行）整理成「段落文本」_src/txt/*.txt，供 convert.py 使用。

处理：去页眉页脚/页码 → 干支易混字订正 → 按标点把折行的段落接回去。
订正只在「上下文明确」时做（相邻地支、干支柱行），不做全局替换。
"""
import re, io, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TXT = os.path.join(ROOT, '_src', 'txt')
GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
# 干支行里常见误识
G_FIX = {'田': '甲', '己': '己', '已': '己', '戍': '戊', '戌': '戊', '成': '戊', '庚': '庚', '康': '庚', '壬': '壬', '王': '壬', '平': '辛', '辜': '辛', '丁': '丁', '了': '丁', '两': '丙', '雨': '丙', '乙': '乙', '己': '己', '关': '癸', '葵': '癸'}
Z_FIX = {'已': '巳', '己': '巳', '卵': '卯', '卬': '卯', '末': '未', '木': '未', '展': '辰', '辱': '辰', '牛': '午', '成': '戌', '戍': '戌', '戊': '戌', '土': '丑', '玄': '亥', '互': '亥', '宙': '寅', '寅': '寅', '子': '子', '于': '子', '酉': '酉', '西': '酉', '由': '申', '甲': '申'}

HEADER = re.compile(r'^(?:[—\-－一]*\s*)?(命理干支奥义|职业象法新解|mingliganzhiaoyi|mingliganzhaoyi|mingzhiganzhiaoyi|[a-zA-Z]{8,})\s*[—\-－一]*$|^\d{1,3}$|^===p\d+===$')
END = '。！？：；”’）)」』.…'


def fix_zhi_context(s):
    # 已 夹在地支之间或后接火/申/酉/亥/午/丑：巳
    s = re.sub(r'(?<=[子丑寅卯辰午未申酉戌亥])已', '巳', s)
    s = re.sub(r'已(?=[子丑寅卯辰午未申酉戌亥火]|[穿合刑冲破])', '巳', s)
    s = re.sub(r'(?<=[甲乙丙丁戊己庚辛壬癸])已(?=[巳酉丑子午未申亥寅卯辰戌])', '己', s)
    s = s.replace('卵', '卯')
    s = re.sub(r'末(?=[土火中穿冲合刑库])', '未', s)
    s = re.sub(r'(?<=[子丑寅卯辰巳午申酉戌亥])末', '未', s)
    return s


DY_MAP = {'两': '丙', '王': '壬', '康': '庚', '日': '巳', '西': '酉', '成': '戌', '戍': '戌', '已': '巳', '末': '未', '卵': '卯', '展': '辰', '牛': '午', '玄': '亥'}


def fix_dayun(l):
    # 大运行：甲辰 乙日 两午 → 甲辰 乙巳 丙午（只在大运行内、「干+支」成对处订正）
    def pair(m):
        g, z = m.group(1), m.group(2)
        g = {'两': '丙', '王': '壬', '康': '庚'}.get(g, g)
        z = DY_MAP.get(z, z)
        return g + z
    return re.sub(r'([甲乙丙丁戊己庚辛壬癸两王康])([子丑寅卯辰巳午未申酉戌亥日西成戍已末卵展牛玄])(?![子丑寅卯辰巳午未申酉戌亥])', pair, l)


def fix_text(l):
    if '大运' in l[:6] or re.match(r'^[甲乙丙丁戊己庚辛壬癸两][子丑寅卯辰巳午未申酉戌亥日西成已末][ \d（(]', l):
        l = fix_dayun(l)
    l = re.sub(r'([乙丁己辛癸])已', r'\1巳', l)
    l = re.sub(r'已(?=[土])', '己', l)
    l = re.sub(r'已(?=[火申酉亥午未子丑寅卯辰戌合穿刑冲破])', '巳', l)
    l = re.sub(r'([甲庚壬丙])成(?![功就长为立])', r'\1戌', l)
    l = re.sub(r'成(?=[土火中])', '戌', l)
    l = re.sub(r'([甲丙庚壬])戊(?![己癸土])', r'\1戌', l)
    l = re.sub(r'两(?=[丁火午申寅辰子戌卯酉未亥])', '丙', l)
    l = re.sub(r'王(?=[申子辰午寅戌水癸亥])', '壬', l)
    l = l.replace('干文', '干支').replace('地文', '地支')
    return l


def fix_pan_line(l):
    """纯天干行 / 纯地支行（4 个字）按位置订正。"""
    t = re.sub(r'[\s　]', '', l)
    if len(t) == 4 and all(c in GAN + ''.join(G_FIX) for c in t) and sum(c in GAN for c in t) >= 2:
        return ''.join(G_FIX.get(c, c) for c in t)
    if len(t) == 4 and all(c in ZHI + ''.join(Z_FIX) for c in t) and sum(c in ZHI for c in t) >= 2:
        return ''.join(Z_FIX.get(c, c) for c in t)
    return l


def reflow(lines):
    out, cur = [], ''
    HEAD = re.compile(r'^(第[一二三四五六七八九十百]+[章节讲期]|例\s*\d|[一二三四五六七八九十]{1,3}[、．.]|[（(][一二三四五六七八九十]+[）)]|乾|坤|大运|【)')
    for l in lines:
        if not l:
            if cur: out.append(cur); cur = ''
            continue
        brk_before = bool(HEAD.match(l)) or len(l) <= 14 and not l.endswith(tuple(END)) and not cur
        if cur and (HEAD.match(l)):
            out.append(cur); cur = ''
        cur += l
        # 短行（≤14 字）且无结束标点：多半是标题或盘行，单独成行
        if cur.endswith(tuple(END)) or (len(cur) <= 16 and not cur.endswith(('，', '、', '：'))):
            out.append(cur); cur = ''
    if cur:
        out.append(cur)
    return out


def process(tag, name):
    raw = io.open(os.path.join(TXT, 'V_%s.txt' % tag), encoding='utf-8').read().split('\n')
    lines = []
    for l in raw:
        l = l.strip()
        if HEADER.match(l):
            if l.startswith('==='):
                lines.append('')
            continue
        l = fix_zhi_context(l)
        l = fix_pan_line(l)
        l = fix_text(l)
        lines.append(l)
    para = reflow(lines)
    io.open(os.path.join(TXT, name + '.txt'), 'w', encoding='utf-8').write('\n'.join(para) + '\n')
    print(tag, len(raw), '→', len(para), '段')


if __name__ == '__main__':
    for tag, name in (('jn', 'S_济南面授班教材'), ('gz', 'S_干支奥义'), ('xf', 'S_职业象法新解'), ('al', 'S_案例集')):
        if os.path.exists(os.path.join(TXT, 'V_%s.txt' % tag)):
            process(tag, name)
