"""验证正文四柱盘吸顶：滚动后盘的 top 应≈50px（顶栏高度）。"""
import json, subprocess, os
CH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
c = json.loads(open('data/data-course.js').read()[len('window.DATA_COURSE='):-2])
n = [x['n'] for x in c if x['title'] == '正局、反局' and x.get('raw')][0]
js = """setTimeout(function(){
 document.querySelector('[data-tab=course]').click();
 setTimeout(function(){
  document.querySelectorAll('.lvg>.qgh')[1].click();
  document.querySelectorAll('.rawg>.qgh').forEach(function(x){if(x.parentNode.dataset.g=='中级#raw')x.click()});
  setTimeout(function(){
   document.querySelector('[data-ch="%d"]').click();
   setTimeout(function(){
    document.querySelectorAll('#chapterBody details.chapter-sec').forEach(function(d){d.open=true});
    var p=document.querySelector('#chapterBody .ichart');
    var pos=getComputedStyle(p).position;
    var y=p.getBoundingClientRect().top+window.scrollY;
    window.scrollTo(0,y+400);
    setTimeout(function(){
      document.title='STICK '+pos+' top='+Math.round(p.getBoundingClientRect().top)+' scrollY='+Math.round(window.scrollY)+' h='+document.body.scrollHeight;
    },300);
   },500);
  },400);
 },400);
},700);""" % n
html = open('index.html').read().replace('</body>', '<script>%s</script></body>' % js)
open('_t_stick.html', 'w').write(html)
r = subprocess.run([CH, '--headless=new', '--disable-gpu', '--window-size=430,900', '--virtual-time-budget=12000', '--dump-dom',
                    'http://localhost:8768/_t_stick.html'], capture_output=True, text=True)
import re
print(re.findall(r'<title>(.*?)</title>', r.stdout))
os.remove('_t_stick.html')
