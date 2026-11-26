#!/usr/bin/env python3
"""精练题库校验：python3 check_fine_questions.py [文件.json ...]（不带参数＝全部）"""
import glob, io, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FQD = os.path.join(ROOT, 'content', '精练题库')
QD = os.path.join(ROOT, 'content', '题目')
TB = os.path.join(ROOT, 'content', '教材')

BAN_Q = re.compile(r'视频|例中|那个命主|这个盘|如上例|本例|上例|该例|此例|上表|上文|本章|讲义|哪份|版本|老师(?:说|认为|讲)|大任|小任|为何断|为什么断|待裁定|存疑')
BAN_OPT = re.compile(r'以上都对|以上都不|都不对|视频')
TYPES = {'rule', 'diff', 'calc', 'xiang', 'step'}


def headings(md):
    hs = []
    for m in re.finditer(r'^#{1,4}\s*(.+)$', md, re.M):
        hs.append(m.group(1).replace('**', '').strip())
    return hs


def norm(s):
    return re.sub(r'[\s*⭐⚠️️]', '', s)


def check(fp):
    errs = []
    rel = os.path.relpath(fp, FQD)[:-5]
    md_path = os.path.join(TB, rel + '.md')
    if not os.path.exists(md_path):
        return ['找不到对应教材 ' + md_path], 0
    md = io.open(md_path, encoding='utf-8').read()
    hs = [norm(h) for h in headings(md)]

    # Load existing end-of-chapter stems to forbid duplicates
    old_stems = set()
    old_qf = os.path.join(QD, rel + '.json')
    if os.path.exists(old_qf):
        try:
            old_stems = {norm(x['q']) for x in json.load(io.open(old_qf, encoding='utf-8'))}
        except Exception:
            pass

    try:
        qs = json.load(io.open(fp, encoding='utf-8'))
    except Exception as ex:
        return ['JSON 解析失败：%s' % ex], 0
    if not isinstance(qs, list):
        return ['顶层必须是数组'], 0
    if not 15 <= len(qs) <= 45:
        errs.append('题数 %d 不在 15–45' % len(qs))

    seen = set()
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
        qn = norm(x['q'])
        if qn in seen:
            errs.append('%s 题干重复' % tag)
        if qn in old_stems:
            errs.append('%s 题干与原章末题重复' % tag)
        seen.add(qn)
        if BAN_Q.search(x['q']):
            errs.append('%s 题干含禁用词/残缺指代：%s' % (tag, BAN_Q.search(x['q']).group(0)))
        for o in opts:
            if BAN_OPT.search(o):
                errs.append('%s 选项含禁用语：%s' % (tag, o))
            if len(o) > 48:
                errs.append('%s 选项过长(%d字)' % (tag, len(o)))
            if not o.strip():
                errs.append('%s 有空选项' % tag)
        if len(x['a']) > 20 and len(x['a']) > 1.3 * max(len(o) for o in w):
            errs.append('%s 正解明显最长' % tag)
        if len(x['e']) < 8 or len(x['e']) > 180:
            errs.append('%s 解析长度 %d 不合适(8–180)' % (tag, len(x['e'])))
        if '〔' in x['e']:
            errs.append('%s 解析里不要自己写〔出处〕' % tag)
        sec = norm(re.sub(r'^#+\s*', '', x['sec']))
        if not sec or not any(h == sec or h.startswith(sec) for h in hs):
            errs.append('%s 小节「%s」在本章标题里找不到' % (tag, x['sec']))
    return errs, len(qs)


if __name__ == '__main__':
    files = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob(os.path.join(FQD, '*', '*.json')))
    total_q = 0
    bad = 0
    for f in files:
        es, n = check(f)
        total_q += n
        if es:
            bad += 1
            print('FAIL', os.path.relpath(f, ROOT), len(es), 'errs:')
            for e in es[:10]:
                print('  -', e)
    print(f'Checked {len(files)} files, {total_q} questions, {bad} files failed')
    sys.exit(1 if bad else 0)
