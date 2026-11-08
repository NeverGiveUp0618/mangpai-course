"""出截图：python3 _shots.py → scratchpad/*.png（需先起 http.server 8767）"""
import json, subprocess, os
S = '/private/tmp/claude-501/-Users-xiaojin/c97bb0b0-4721-456d-a7d3-34ed88eae97b/scratchpad/'
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
c = json.loads(open('data/data-course.js').read()[len('window.DATA_COURSE='):-2])
n = [x['n'] for x in c if x['title'] == '正局、反局' and x.get('raw')][0]
base = open('index.html').read()


def page(name, js):
    open('_t_%s.html' % name, 'w').write(base.replace('</body>', '<script>setTimeout(function(){%s},700)</script></body>' % js))
    subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=430,900', '--virtual-time-budget=9000',
                    '--screenshot=' + S + name + '.png', 'http://localhost:8767/_t_%s.html' % name],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove('_t_%s.html' % name)


page('home2', '')
page('course2', "document.querySelector('[data-tab=course]').click()")
page('chap2', "document.querySelector('[data-tab=course]').click();setTimeout(function(){var g=document.querySelectorAll('.lvg>.qgh')[1];g.click();var r=document.querySelectorAll('.rawg>.qgh');r.forEach(function(x){if(x.parentNode.dataset.g=='中级#raw')x.click()});setTimeout(function(){document.querySelector('[data-ch=\"%d\"]').click();setTimeout(function(){var h=document.querySelector('#chapterBody h2');if(h)h.click();setTimeout(function(){var p=document.querySelectorAll('#chapterBody .ichart')[0];if(p)window.scrollTo(0,Math.max(0,p.getBoundingClientRect().top+window.scrollY-60+250))},300)},400)},400)},300)" % n)
