# -*- coding: utf-8 -*-
"""讲解文字排版：把成坨的原文拆成短段、列表，并把「X Y 作用」「干支运/年」加粗，便于手机阅读。"""
import re

GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
ENUM = re.compile(r'^(?:[⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽①②③④⑤⑥⑦⑧⑨⑩]|[（(][一二三四五六七八九十\d]+[）)]|\d{1,2}\s*[、．.])\s*')
OPEN, CLOSE = '（(「『“《', '）)」』”》'
END = '。！？；'
PAIR = re.compile(r'(?<![\*\w])([%s]{2}(?:暗合|半合|合|冲|穿|刑|破|害|拱))(?!\*)' % ZHI)
LUCK = re.compile(r'(?<![\*\w])([%s][%s](?:运|年|月|日|时))(?!\*)' % (GAN, ZHI))


def split_sent(t):
    out, buf, depth = [], '', 0
    for ch in t:
        buf += ch
        if ch in OPEN:
            depth += 1
        elif ch in CLOSE:
            depth = max(0, depth - 1)
        elif ch in END and depth == 0:
            out.append(buf)
            buf = ''
    if buf.strip():
        out.append(buf)
    return out


def emph(s):
    if '**' in s:
        return s
    s = PAIR.sub(r'**\1**', s)
    s = LUCK.sub(r'**\1**', s)
    return s


def beautify(text, target=58, bold=True):
    """返回 markdown：短段 + 列表项。"""
    t = re.sub(r'[ \t　]+', ' ', text.replace('\n', ' ')).strip()
    if not t:
        return ''
    blocks, cur, lst = [], '', []

    def flush_cur():
        nonlocal cur
        if cur.strip():
            blocks.append(emph(cur.strip()) if bold else cur.strip())
        cur = ''

    def flush_lst():
        nonlocal lst
        if lst:
            blocks.append('\n'.join('- ' + (emph(x) if bold else x) for x in lst))
        lst = []

    for s in split_sent(t):
        s = s.strip()
        if not s:
            continue
        if ENUM.match(s):
            flush_cur()
            lst.append(ENUM.sub('', s).strip())
            continue
        if lst and len(lst[-1]) < 120 and not s.endswith(('：', ':')):
            lst[-1] += s          # 列表项的后续句子并进该项
            continue
        flush_lst()
        cur += s
        if len(cur) >= target or s.endswith(('：', ':')):
            flush_cur()
    flush_cur()
    flush_lst()
    return '\n\n'.join(blocks)
