"""Validated reading diagrams; branches do not silently become causal proof."""
import hashlib, html, re


def render_reasoning_map(item, row, text):
    assert item['caseId'] == row['caseId'] and item['order'] == row['order']
    assert item['bodySha256'] == hashlib.sha256(text.encode()).hexdigest(), ('结构图正文已变，须重新核图', row['order'])
    assert item['layout'] in ('chain', 'parallel', 'compare', 'timeline', 'branches')
    nodes = item['nodes']
    assert 2 <= len(nodes) <= 7
    authored = item['basis'] == 'authored-reading-map'
    esc = html.escape
    cards = []
    for i, node in enumerate(nodes, 1):
        assert node['kind'] in ('reason', 'counter', 'limit') and node['heading'] and node['text']
        if not authored:
            # Excerpt maps never synthesize an unseen causal edge.
            normalized = lambda s: re.sub(r'[\s*`>#]', '', s)
            assert normalized(node['text']) in normalized(text), (row['order'], node)
        jump = '' if authored else '<button type="button" class="crm-jump" data-cr-jump="%s">看这一段</button>' % esc(node['heading'], quote=True)
        cards.append('<div class="crm-node crm-%s"><span class="crm-number">%s</span><div><strong>%s</strong><span class="crm-text">%s</span>%s</div></div>' % (node['kind'], i, esc(node['heading']), esc(node['text']), jump))
    labels = {'chain': '逐步追踪', 'parallel': '分路看作用', 'compare': '对照与排除', 'timeline': '原局与岁运', 'branches': '疑点与边界'}
    caption = '推演结构图' if authored else '本篇阅读结构'
    note = ('图中的推理依正文及对照原段展开；反证与未解条件也在图内，不把箭头当作额外证明。' if authored else '摘取本篇段落原句，帮助找阅读路径；分支和排列不额外证明因果，点卡片下方可跳到对应讲解。')
    return '<details class="reasoning-map" data-map-basis="%s"%s><summary>%s<span>%s</span></summary><figure class="crm-figure"><figcaption>%s</figcaption><div class="crm-nodes crm-%s">%s</div><div class="crm-note">%s</div></figure></details>' % (esc(item['basis']), ' open' if authored else '', caption, labels[item['layout']], esc(item['title']), item['layout'], ''.join(cards), esc(note))
