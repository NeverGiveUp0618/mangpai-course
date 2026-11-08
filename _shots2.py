import json, subprocess, os, sys
S = '/private/tmp/claude-501/-Users-xiaojin/c97bb0b0-4721-456d-a7d3-34ed88eae97b/scratchpad/'
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
port = sys.argv[1] if len(sys.argv) > 1 else '8771'
base = open('index.html').read()
c = json.loads(open('data/data-course.js').read()[len('window.DATA_COURSE='):-2])
n = [x['n'] for x in c if x['title'].startswith('入手方法') and not x.get('raw')][0]
js = """setTimeout(function(){document.querySelector('[data-tab=course]').click();setTimeout(function(){document.querySelector('[data-ch="%d"]').click();setTimeout(function(){var ds=document.querySelectorAll('#chapterBody details.chapter-sec');ds.forEach(function(d){d.open=true});var p=document.querySelectorAll('#chapterBody .ichart');var k=0;for(var i=0;i<p.length;i++){if(p[i].querySelector('.dys')){k=i;break}}},500)},400)},700)""" % n
open('_t_s2.html', 'w').write(base.replace('</body>', '<script>%s</script></body>' % js))
subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=430,2600', '--virtual-time-budget=9000',
                '--screenshot=' + S + 's2.png', 'http://localhost:%s/_t_s2.html' % port], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.remove('_t_s2.html')
