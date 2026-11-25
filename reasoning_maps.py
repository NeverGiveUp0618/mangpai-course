"""Inline text diagrams, following the companion course's pre/code presentation."""
import hashlib
import html


def render_reasoning_map(item, row, text):
    assert item['caseId'] == row['caseId'] and item['order'] == row['order']
    assert item['bodySha256'] == hashlib.sha256(text.encode()).hexdigest(), ('正文已变，须重新核图', row['order'])
    assert item['basis'] == 'authored-reading-map'
    flow = item['flow']
    assert len(flow.splitlines()) >= 5 and ('→' in flow or '↓' in flow)
    return '<div class="reasoning-map"><pre><code>%s</code></pre></div>' % html.escape(flow)
