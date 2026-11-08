import json, re, subprocess, os, sys
S = '/private/tmp/claude-501/-Users-xiaojin/c97bb0b0-4721-456d-a7d3-34ed88eae97b/scratchpad/'
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
port = sys.argv[1]
css = sys.argv[2] if len(sys.argv) > 2 else 'style.css'
c = json.loads(open('data/data-course.js').read()[len('window.DATA_COURSE='):-2])
html = ''
k = 0
for x in c:
    if x['raw']:
        continue
    for m in re.finditer(r'<div class="ichart">.*?</div></div>(?:<div class="dys">.*?</div></div>)?', x['html']):
        if 'dys' in m.group(0) and k < 2:
            html += m.group(0) + '<p>这是盘下面的一段讲解文字，用来看吸顶效果与间距。</p>'
            k += 1
        if k >= 2:
            break
    if k >= 2:
        break
page = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=430"><link rel=stylesheet href="%s"><body><div style="padding:14px"><div class="doc">%s</div></div></body>' % (css, html)
open('_t_s3.html', 'w').write(page)
subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=430,420', '--screenshot=' + S + 's3.png', 'http://localhost:%s/_t_s3.html' % port], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.remove('_t_s3.html')
