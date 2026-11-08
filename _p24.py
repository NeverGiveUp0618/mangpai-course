import os
p = os.path.join('..', 'bazi-course', 'style.css')
s = open(p, encoding='utf-8').read()
if '四柱盘：五行色牌' in s:
    print('已加过')
    raise SystemExit
conts = ['.doc .ichart .c', '.sticky-chart .c', '.vchart', '.vpluck .c']
ab = ',\n'.join('%s .a,%s .b' % (c, c) if not c.endswith('.vchart') else '.vchart .a,.vchart .b' for c in conts)
css = '\n/* ===== 四柱盘：五行色牌（2026-11-08 统一设计，仅样式，不动内容） ===== */\n'
css += ab + '''{
  display:block; margin:2px auto 0; width:28px; height:28px; line-height:28px; border-radius:8px;
  text-align:center; font-size:17px; font-weight:700; background:var(--bg2); box-shadow:inset 0 0 0 1px var(--line)
}
'''
for w, pct in (('mu', 16), ('huo', 16), ('tu', 16), ('jin', 18), ('shui', 16)):
    sel = ',\n'.join(['.doc .ichart .c .a.w-%s,.doc .ichart .c .b.w-%s' % (w, w), '.sticky-chart .c .a.w-%s,.sticky-chart .c .b.w-%s' % (w, w),
                      '.vchart .a.w-%s,.vchart .b.w-%s' % (w, w), '.vpluck .a.w-%s,.vpluck .b.w-%s' % (w, w)])
    css += sel + '{background:color-mix(in srgb,var(--wx-%s) %d%%,transparent); box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--wx-%s) 45%%,transparent)}\n' % (w, pct, w)
css += '''.doc .ichart .c.day,.sticky-chart .c.day{background:none; box-shadow:none; outline:none}
.vchart .c{min-width:30px}
.vpluck .c{min-width:28px}
.vchart .ss{margin-top:2px}
'''
open(p, 'w', encoding='utf-8').write(s + css)
print('旧站 CSS 已追加')
