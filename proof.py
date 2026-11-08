# -*- coding: utf-8 -*-
# 排盘校对：阴阳配对 + 五虎遁（月柱）+ 五鼠遁（时柱）。识别/抄写错字多半会同时破坏这三条。
import itertools

GAN = '甲乙丙丁戊己庚辛壬癸'
ZHI = '子丑寅卯辰巳午未申酉戌亥'
GCONF = {'戌': '戊', '戍': '戊', '成': '戊', '已': '己', '巳': '己', '王': '壬', '康': '庚', '两': '丙', '雨': '丙', '了': '丁'}
ZCONF = {'已': '巳', '己': '巳', '卵': '卯', '卬': '卯', '末': '未', '展': '辰', '牛': '午', '戊': '戌', '戍': '戌', '成': '戌', '西': '酉', '玄': '亥', '于': '子'}
STAT = {'ok': 0, 'fixed': [], 'bad': []}


def valid(g, z):
    try:
        gi = [GAN.index(c) for c in g]
        zi = [ZHI.index(c) for c in z]
    except ValueError:
        return False
    if not all((a - b) % 2 == 0 for a, b in zip(gi, zi)):
        return False
    mbase = [2, 4, 6, 8, 0][gi[0] % 5]
    if gi[1] != (mbase + (zi[1] - 2) % 12) % 10:
        return False
    hbase = [0, 2, 4, 6, 8][gi[2] % 5]
    return gi[3] == (hbase + zi[3]) % 10 or (zi[3] == 0 and gi[3] == (hbase + 2) % 10)


def repair(gan, zhi):
    """返回 (gan, zhi, 状态)；状态 ok / fixed / bad。"""
    g = ''.join(c if c in GAN else GCONF.get(c, c) for c in gan)
    z = ''.join(c if c in ZHI else ZCONF.get(c, c) for c in zhi)
    if len(g) != 4 or len(z) != 4 or any(c not in GAN for c in g) or any(c not in ZHI for c in z):
        return gan, zhi, 'bad'
    if valid(g, z):
        return g, z, ('ok' if (g, z) == (gan, zhi) else 'fixed')
    found = set()
    for n in (1, 2):
        for idx in itertools.combinations(range(8), n):
            pools = [GAN if i < 4 else ZHI for i in idx]
            for rep in itertools.product(*pools):
                gg, zz = list(g), list(z)
                for i, c in zip(idx, rep):
                    if i < 4:
                        gg[i] = c
                    else:
                        zz[i - 4] = c
                if valid(''.join(gg), ''.join(zz)):
                    found.add((''.join(gg), ''.join(zz)))
        if len(found) == 1:
            a, b = next(iter(found))
            return a, b, 'fixed'
        if len(found) > 1:
            return g, z, 'bad'
    return g, z, 'bad'
