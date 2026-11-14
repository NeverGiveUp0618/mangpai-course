#!/usr/bin/env python3
"""章末题目校验：python3 check_questions.py [文件.json ...]（不带参数＝全部）
结构、小节标题存在、禁用词、残缺指代、选项长度/重复、引文出现在本章。零错误才算通过。"""
import io, json, os, re, sys, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
QD = os.path.join(ROOT, 'content', '题目')
TB = os.path.join(ROOT, 'content', '教材')

BAN_Q = re.compile(r'视频|例中|那个命主|这个盘|如上例|本例|上例|该例|此例|上表|上文|本章|讲义|哪份|版本|老师(?:说|认为|讲)|大任|小任|为何断|为什么断|待裁定|存疑')
BAN_OPT = re.compile(r'以上都对|以上都不|都不对|视频')
TYPES = {'rule', 'diff', 'calc', 'xiang', 'step'}


def headings(md):
    hs = []
    for m in re.finditer(r'^#{1,4}\s*(.+)$', md, re.M):
        hs.append(re.sub(r'[*⭐⚠️\s]+', '', m.group(1)) if False else m.group(1).replace('**', '').strip())
    return hs


def norm(s):
    return re.sub(r'[\s*⭐⚠️️]', '', s)


def check(fp):
    errs = []
    rel = os.path.relpath(fp, QD)[:-5]
    md_path = os.path.join(TB, rel + '.md')
    if not os.path.exists(md_path):
        return ['找不到对应教材 ' + md_path], 0
    md = io.open(md_path, encoding='utf-8').read()
    hs = [norm(h) for h in headings(md)]
    body = norm(md)
    try:
        qs = json.load(io.open(fp, encoding='utf-8'))
    except Exception as ex:
        return ['JSON 解析失败：%s' % ex], 0
    if not isinstance(qs, list):
        return ['顶层必须是数组'], 0
    if not 5 <= len(qs) <= 12:
        errs.append('题数 %d 不在 5–12' % len(qs))
    seen = set()
    secs = {}
    for i, x in enumerate(qs):
        tag = '#%d %s' % (i + 1, str(x.get('q', ''))[:18])
        for k in ('t', 'q', 'a', 'w', 'e', 'sec'):
            if k not in x:
                errs.append('%s 缺字段 %s' % (tag, k))
        if any(k not in x for k in ('t', 'q', 'a', 'w', 'e', 'sec')):
            continue
        if x['t'] not in TYPES:
            errs.append('%s 题型 %s 不合法' % (tag, x['t']))
        w = x['w']
        if not isinstance(w, list) or len(w) != 3 or len(set(w)) != 3:
            errs.append('%s 干扰项必须是 3 个互不相同的' % tag)
            continue
        opts = [x['a']] + w
        if len(set(opts)) != 4:
            errs.append('%s 选项有重复/正解混入干扰项' % tag)
        if x['q'] in seen:
            errs.append('%s 题干重复' % tag)
        seen.add(x['q'])
        if BAN_Q.search(x['q']):
            errs.append('%s 题干含禁用词/残缺指代：%s' % (tag, BAN_Q.search(x['q']).group(0)))
        for o in opts:
            if BAN_OPT.search(o):
                errs.append('%s 选项含禁用语：%s' % (tag, o))
            if len(o) > 40:
                errs.append('%s 选项过长(%d字)' % (tag, len(o)))
            if not o.strip():
                errs.append('%s 有空选项' % tag)
        if len(x['a']) > 20 and len(x['a']) > 1.3 * max(len(o) for o in w):
            errs.append('%s 正解明显最长' % tag)
        if len(x['e']) < 8 or len(x['e']) > 160:
            errs.append('%s 解析长度 %d 不合适(8–160)' % (tag, len(x['e'])))
        if '〔' in x['e']:
            errs.append('%s 解析里不要自己写〔出处〕' % tag)
        sec = norm(re.sub(r'^#+\s*', '', x['sec']))
        if not sec or not any(h == sec or h.startswith(sec) for h in hs):
            errs.append('%s 找不到小节标题「%s」' % (tag, x['sec']))
        secs[x['sec']] = secs.get(x['sec'], 0) + 1
        # 题干/答案里「」引文应出现在本章
        for m in re.finditer(r'「([^」]{4,})」', x['q'] + '｜' + x['a'] + '｜' + x['e']):
            qq = norm(m.group(1))
            if '（' in qq and '）' in qq and '　' in m.group(1):
                continue
            if qq not in body:
                errs.append('%s 引文在本章找不到：「%s」' % (tag, m.group(1)[:24]))
    # 答案最长比例（只看总体，偏高提醒）
    if qs and all(isinstance(x.get('w'), list) and len(x['w']) == 3 for x in qs):
        longest = sum(1 for x in qs if len(x['a']) > max(len(o) for o in x['w']))
        if len(qs) >= 6 and longest / len(qs) > 0.5:
            errs.append('正解最长占 %d/%d，超过一半，干扰项要补长/正解要缩短' % (longest, len(qs)))
    if len(secs) < 2 and len(qs) >= 6:
        errs.append('所有题都集中在一个小节')
    return errs, len(qs)


def main():
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(QD, '*', '*.json')))
    bad = tot = 0
    for fp in files:
        e, n = check(fp)
        tot += n
        if e:
            bad += 1
            print('❌', os.path.relpath(fp, QD))
            for s in e:
                print('    ', s)
    print('%d 个文件 / %d 题；有问题 %d 个文件' % (len(files), tot, bad))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
