p = 'build_mp.py'
b = open(p).read()
if 'THEMES' not in b:
    a = b.index('def build_outline(')
    e = b.index('def main():')
    new = '''THEMES = [
    ('体系总览与宫位', ['盲派体系总览', '宫位取象'], ['天道、阴阳', '十神与宫位', '宫位类象'], ['体用宾主']),
    ('十神与类象', ['十神类象'], ['干支类象', '宫位类象与十神'], ['宫位、十神、神煞类象深化', '干支象义']),
    ('干支与虚实', ['十天干', '干支配置'], ['十天干象义', '干支关系', '十二地支象义', '干支虚实'], []),
    ('合', ['合（一）', '合（二）', '合（三）'], ['地支作用'], ['天干五合与地支六合']),
    ('冲、穿、刑、破、墓', ['刑、破、害、墓', '冲、穿（一）', '冲、穿（二）'], [], ['三合、六冲']),
    ('做功与效率', ['做功方式'], ['象的应用'], ['能量效率']),
    ('正局与反局', ['基础问题'], ['正局与反局'], ['正局反局进阶']),
    ('入手与层次', ['入手方法'], [], []),
    ('大运流年与应期', ['应期入门'], ['应期'], ['大运流年与应期']),
    ('财与官', [], ['财命专辑', '官命看法'], ['财命的高级断法', '官命、职业与学历']),
    ('婚姻', ['婚姻与看寿'], ['婚姻专辑'], ['婚姻宫', '恋爱同居', '男命多婚', '女命多婚', '婚外情', '包局婚姻', '配偶情况', '伤克配偶', '独身组合', '差婚姻']),
    ('六亲（父母）', [], [], ['父母死亡', '父母离异']),
    ('学历、牢狱与实战', [], ['学历与牢狱', '实战演示'], []),
    ('职业象法', [], [], ['职业象法']),
]


def build_outline(courses, notes, quiz):
    def find(lv, prefixes):
        out = []
        for pre in prefixes:
            for c in courses:
                if c['level'] == lv and not c['raw'] and c['title'].startswith(pre) and c not in out:
                    out.append(c)
        return out

    def links(cs):
        return '<br>'.join('<a class="chlink" data-ch="%d">%s</a>' % (c['n'], c['title']) for c in cs) or '—'
    h = ['<h1 id="学习路线">学习路线</h1>',
         '<blockquote><p><strong>怎么学</strong>：先读完初级（建立体系），再按需要进中级、高级；同一个主题在三级里是<strong>由浅入深</strong>的同一条线，下面按主题横向对照，一眼看到该主题三级各读哪几章。读完一章，回「练」里做对应主题的命例。</p></blockquote>',
         '<p><strong>收录范围</strong>：只收盲派体系<strong>成熟期</strong>的资料；早期仍用用神的口径只作对照（命例里标「早期口径」）。教材是改写整理稿，逐字原稿收在课程页各级下的「原稿讲义」里。</p>',
         '<h2 id="主题对照">按主题对照</h2>',
         '<div class="tw"><table><thead><tr><th>主题</th><th>初级</th><th>中级</th><th>高级</th></tr></thead><tbody>']
    for name, a, b2, c3 in THEMES:
        h.append('<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            name, links(find('初级', a)), links(find('中级', b2)), links(find('高级', c3))))
    h.append('</tbody></table></div>')
    h.append('<h2 id="顺序">建议顺序</h2><ol><li><strong>初级</strong>：按章顺序通读（18 章），重点是体系总览、宫位、十神、干支配置、合冲穿刑破墓、做功方式。</li>'
             '<li><strong>中级</strong>：先读「干支奥义」七章打牢象义，再读正局反局、应期、类象与象的应用，最后读财官婚学牢专辑。</li>'
             '<li><strong>高级</strong>：先读作用方式深论、体用宾主与能量效率，再按需要读婚姻六亲与职业象法。</li></ol>')
    return ''.join(h)


'''
    b = b[:a] + new + b[e:]
    open(p, 'w').write(b)

# app：学习路线里的章节链接
p = '_patch_app.py'
s = open(p).read()
if 'chlink' not in s:
    marker = "io.open(p, 'w', encoding='utf-8').write(s)\n\n# ───── index.html"
    add = r'''s = s.replace("  $('#outlineBody').innerHTML = META.outline || '';\n  bindDoc($('#outlineBody'));", "  $('#outlineBody').innerHTML = META.outline || '';\n  bindDoc($('#outlineBody'));\n  $$('#outlineBody .chlink').forEach(function (a) { a.onclick = function () { show('chapter', +a.dataset.ch); }; });", 1)
'''
    s = s.replace(marker, add + marker, 1)
    open(p, 'w').write(s)
p = 'style.css'
c = open(p).read()
if '.chlink' not in c:
    c += '\n.chlink{color:var(--indigo);cursor:pointer;border-bottom:1px dashed var(--indigo);font-size:13px;line-height:1.9;white-space:normal}\n.doc td{vertical-align:top}\n'
    open(p, 'w').write(c)
print('ok')
