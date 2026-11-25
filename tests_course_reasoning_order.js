/* Course AI belongs after the original case analysis, never between chart and analysis. */
const fs=require('fs'),vm=require('vm'),assert=require('assert'),{JSDOM}=require('jsdom');
const source=fs.readFileSync('app.js','utf8');
const code=source.slice(source.indexOf('function chapterReasoningAnchor('),source.indexOf('function addChapterExtras('));
let checks=0;const ok=(value,message)=>{assert(value,message);checks++;};
function setup(html){
 const dom=new JSDOM('<main id="root">'+html+'</main>'),d=dom.window.document,root=d.querySelector('#root');
 const api=new Function('document','$$','needQuiz','show',code+';return {attach:attachChapterReasoning,anchor:chapterReasoningAnchor};')(d,(s,r)=>[...(r||d).querySelectorAll(s)],()=>Promise.resolve({items:[]}),()=>{});
 return {dom,root,api};
}
const chart=n=>`<div class="ichart" data-case-id="case${n}" data-case-n="${n}">命盘${n}</div>`;
function fixture(name,html,expected){
 const {dom,root,api}=setup(html);api.attach(root);
 for(const [n,id] of Object.entries(expected)){const wrap=root.querySelector('.ch-rs-wrap[data-case-n="'+n+'"]'),end=root.querySelector('#'+id);ok(!!wrap&&!!end,name+' 存在入口及分析');ok(!!(end.compareDocumentPosition(wrap)&4),name+' AI在完整原文分析后');}
 const count=root.querySelectorAll('.ch-rs-wrap').length;api.attach(root);ok(root.querySelectorAll('.ch-rs-wrap').length===count,name+' 重复绑定不重复插入');dom.window.close();
}
fixture('分析及反馈连续多段','<h3>例一</h3>'+chart(1)+'<p>原文分析首段</p><ol><li>逐项分析</li></ol><p id="end">实际反馈</p><h3>例二</h3>'+chart(2)+'<p id="end2">第二例分析</p>',{1:'end',2:'end2'});
fixture('分析子标题与运年','<h3>命例一</h3>'+chart(1)+'<h4>分析</h4><p>原局</p><h4>运年应期</h4><ul><li>某年反馈</li></ul><p id="end">婚姻补充</p><h3>命例二</h3>',{1:'end'});
fixture('先列两盘再共同分析','<h3>命例对比</h3>'+chart(1)+chart(2)+'<p id="shared">两盘共同的原文分析</p><h2>下一节</h2>',{1:'shared',2:'shared'});
fixture('各盘有各自分析',chart(1)+'<p id="a">第一盘原解</p>'+chart(2)+'<p id="b">第二盘原解</p>',{1:'a',2:'b'});
fixture('段落形式的下例标记',chart(1)+'<p id="end">前例分析</p><p>例2.</p>'+chart(2)+'<p id="end2">后例分析</p>',{1:'end',2:'end2'});
fixture('无原解不跨入下例','<h3>例一</h3>'+chart(1)+'<p id="dy">大运：甲子 乙丑</p><h3>例二</h3>'+chart(2)+'<p id="end">后例原解</p>',{1:'dy',2:'end'});
fixture('两盘间保留乾造标签',chart(1)+'<p>乾造</p>'+chart(2)+'<p id="both">两盘对照原文分析</p>',{1:'both',2:'both'});
fixture('乾造开头的分析不是下例标题',chart(1)+'<p id="analysis">乾造以财为妻，原文分析继续。</p><h2>下一节</h2>',{1:'analysis'});
const sandbox={window:{}};
for(const f of ['data-course','data-raw','data-body-chu','data-body-zhong','data-body-gao','data-body-zhuan'])vm.runInNewContext(fs.readFileSync('data/'+f+'.js','utf8'),sandbox);
const W=sandbox.window,counts={textbook:0,raw:0},report=[],noAnalysis=[];let total=0,withFollowingText=0;
for(const c of W.DATA_COURSE){
 const val=[W.DATA_RAW,W.DATA_BODY_chu,W.DATA_BODY_zhong,W.DATA_BODY_gao,W.DATA_BODY_zhuan].map(v=>v&&v[c.id]).find(Boolean);
 const html=c.html||(val&&val.html);assert(typeof html==='string','课程正文缺失 '+c.id);
 const {dom,root,api}=setup(html);
 const foldSource=source.slice(source.indexOf('function foldChapterSections('),source.indexOf('function openChapterFold('));
 const fold=new Function('document','ls','K','$$','save',foldSource+';return foldChapterSections;')(dom.window.document,()=>({}),{fold:'test'},(s,r)=>[...r.querySelectorAll(s)],()=>{});
 fold(root,c.id);
 const before=root.innerHTML,charts=[...root.querySelectorAll('.ichart[data-case-id]')];
 const originals=charts.map(ch=>{let end=ch;for(let n=ch.nextElementSibling;n;n=n.nextElementSibling){if(/^H[1-6]$/.test(n.tagName)||n.tagName==='HR'||n.matches('.ichart')||n.querySelector('.ichart')||/^(?:\d+(?:\.\d+)*\s*)?(?:命例|案例|例\s*[一二三四五六七八九十\d]|[乾坤]造|另一造|对照造)/.test(n.textContent.trim()))break;end=n;}return {chart:ch,end};});
 api.attach(root);const wraps=[...root.querySelectorAll('.ch-rs-wrap')];ok(wraps.length===charts.length,c.id+' 每处命例恰好一个入口');
 ok(wraps.every(w=>w.querySelector('.ch-rs-box').hidden&&w.querySelector('button').getAttribute('aria-expanded')==='false'),c.id+' AI全部默认折叠，需手动展开');
 for(const {chart:ch,end} of originals){const wrap=ch._chapterReasoningWrap;ok(!!wrap&&wrap.dataset.caseId===ch.dataset.caseId,c.id+' 对应固定命例ID不变');ok(!!(end.compareDocumentPosition(wrap)&4),c.id+' 命例'+ch.dataset.caseN+' 原有连续分析块均在AI前；应在 '+end.textContent.slice(0,130)+' 后，实际在 '+wrap.previousElementSibling.textContent.slice(0,130)+' 后');if(end!==ch)withFollowingText++;}
 api.attach(root);ok(root.querySelectorAll('.ch-rs-wrap').length===charts.length,c.id+' 不重复插入口');
 wraps.forEach(w=>w.remove());ok(root.innerHTML===before,c.id+' 原课程文字、命盘、分析顺序逐字不变');
 for(const ch of charts){if(api.anchor(ch)===ch)noAnalysis.push({chapter:c.n,caseN:ch.dataset.caseN,next:ch.nextElementSibling?.textContent.slice(0,100)});}
 total+=charts.length;counts[c.raw?'raw':'textbook']++;report.push({id:c.id,n:c.n,title:c.title,raw:!!c.raw,charts:charts.length});dom.window.close();
}
ok(counts.textbook===78&&counts.raw===85,'78教材与85原稿全量检查');ok(total===3363,'3363处既有匹配命盘全部处理，不增不减');
if(fs.existsSync('_src/course_reasoning_order'))fs.writeFileSync('_src/course_reasoning_order/audit.json',JSON.stringify({total,counts,withFollowingText,checks,noAnalysis,courses:report},null,2));
console.log(`通过 ${checks} 项；78教材＋85原稿、${total}处AI入口，原分析在前且原文不改；${withFollowingText}处核对连续原文块。`);
