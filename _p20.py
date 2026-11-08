import io
p='content/教材/高级/24-女命多婚组合.md'; s=io.open(p,encoding='utf-8').read()
s=s.replace('（原稿提示此盘干支组合不合历法，待校，大运栏为庚戌起、2岁起运，仅供参考。）','')
io.open(p,'w',encoding='utf-8').write(s)
p='content/教材/初级/12-婚姻与看寿入门.md'; L=io.open(p,encoding='utf-8').read().split('\n')
L=[l for l in L if '此盘干支组合不合历法' not in l and '原稿已标注干支不合历法' not in l]
io.open(p,'w',encoding='utf-8').write('\n'.join(L))
