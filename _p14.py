import sys, io, contextlib
sys.path.insert(0, '.')
from proof import valid
with contextlib.redirect_stdout(io.StringIO()):
    import verify_textbook as v
near = []; far = []
for lv, fn, k in v.missing_pans:
    g, z = k.split('/')
    best = min((sum(a != b for a, b in zip(g + z, r.replace('/', ''))) for r in v.rawpans), default=9)
    (near if best <= 2 else far).append((lv, fn, k, best, valid(g, z)))
print('近似匹配(≤2字差)', len(near), ' 无近似', len(far))
for x in far:
    print(x)
