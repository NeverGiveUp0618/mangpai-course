"""Validated reading diagrams; branches do not silently become causal proof."""
import hashlib, html


def render_reasoning_map(item, row, text):
    assert item['caseId'] == row['caseId'] and item['order'] == row['order']
    assert item['bodySha256'] == hashlib.sha256(text.encode()).hexdigest(), ('结构图正文已变，须重新核图', row['order'])
    assert item['layout'] in ('chain', 'parallel', 'compare', 'timeline', 'branches')
    nodes = item['nodes']
    assert 2 <= len(nodes) <= 7
    assert item['basis'] == 'authored-reading-map', '只保留专门设计的推演图'
    esc = html.escape
    cards = []
    for i, node in enumerate(nodes, 1):
        assert node['kind'] in ('reason', 'counter', 'limit') and node['heading'] and node['text']
        cards.append('<div class="crm-node crm-%s"><span class="crm-number">%s</span><div><strong>%s</strong><span class="crm-text">%s</span></div></div>' % (node['kind'], i, esc(node['heading']), esc(node['text'])))
    labels = {'chain': '逐步追踪', 'parallel': '分路看作用', 'compare': '对照与排除', 'timeline': '原局与岁运', 'branches': '疑点与边界'}
    caption = '盘源核对图' if item['order'] in (889, 926) else '推演结构图'
    note = '原文明文、AI推断与待核缺口依正文区分；图不补出资料中没有的条件。'
    return '<details class="reasoning-map" data-map-basis="%s"%s><summary>%s<span>%s</span></summary><figure class="crm-figure"><figcaption>%s</figcaption><div class="crm-nodes crm-%s">%s</div><div class="crm-note">%s</div></figure></details>' % (esc(item['basis']), ' open', caption, labels[item['layout']], esc(item['title']), item['layout'], ''.join(cards), esc(note))
