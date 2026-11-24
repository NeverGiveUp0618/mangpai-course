/* Five-case pilot: content boundaries, progression, source return and search. */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert'),crypto=require('crypto'),{JSDOM}=require('jsdom');
let checks=0;const ok=(v,m)=>{assert(v,m);checks++;console.log('✓',m)};
const sandbox={window:{}};vm.runInNewContext(fs.readFileSync('data/data-quiz.js','utf8'),sandbox);const qs=sandbox.window.DATA_QUIZ.items,manifest=JSON.parse(fs.readFileSync('content/命例拆解/目录.json'));
ok(qs.length===936&&manifest.length===5,'只补五例，命例总量936不变');
const original=qs.map(q=>{const c={...q};delete c.reasoningOrder;delete c.reasoningTitle;c.chai=c.chai.split('<hr><section class="case-reasoning"')[0];return c;});
ok(crypto.createHash('sha256').update(JSON.stringify(original)).digest('hex')==='f019609c13cfecb31e2590f22977d464ebdfb74549cbf150c22deedacdaa30ca','原936命例的ID、原断原解、盘、大运、学习关联及基础拆解完整保留');
const pilot=qs.filter(q=>q.reasoningOrder).sort((a,b)=>a.reasoningOrder-b.reasoningOrder);
ok(pilot.length===5&&pilot.map(q=>q.id).join('|')===manifest.map(q=>q.caseId).join('|'),'五个固定ID与审阅顺序一致');
for(const q of pilot){ok(q.chai.includes('class="case-reasoning"')&&q.chai.includes('AI推理拆解')&&q.chai.includes('推断')&&q.chai.includes('核对依据短句'),'命例'+q.n+'有实质推理、推断标识及核对依据');}
ok(pilot[4].chai.includes('壬的具体作用暂留问题')&&pilot[3].chai.includes('局部之功与全局之净'),'保留未解问题，不把局部净扩大成全局净');
const html=fs.readFileSync('index.html','utf8').replace(/<link rel="stylesheet"[^>]*>/g,'');const dom=new JSDOM(html,{url:'https://x.test/mangpai-course/',runScripts:'outside-only',pretendToBeVisual:true});const w=dom.window,d=w.document,errors=[];w.scrollTo=()=>{};w.matchMedia=()=>({matches:false,addListener(){},removeListener(){}});w.addEventListener('error',e=>errors.push(e.message));
for(const file of ['data-meta','data-course','data-notes','data-quiz','data-raw','data-ref','data-st','data-qna','data-plain','data-body-chu','data-body-zhong','data-body-gao','data-body-zhuan'])w.eval(fs.readFileSync('data/'+file+'.js','utf8'));
w.eval(`window.__create=document.createElement.bind(document);document.createElement=function(t){let e=window.__create(t);if(t==='script')Object.defineProperty(e,'src',{set(v){setTimeout(()=>e.onload&&e.onload(),0)}});return e;}`);w.eval(fs.readFileSync('app.js','utf8'));
const wait=ms=>new Promise(r=>setTimeout(r,ms)),click=e=>{assert(e,'missing element');e.dispatchEvent(new w.MouseEvent('click',{bubbles:true}))},$=s=>d.querySelector(s);
(async()=>{
await wait(50);click($('[data-tab="qlist"]')||$('[data-go="qlist"]'));await wait(100);click($('[data-m="reasoning"]'));await wait(60);
ok(d.querySelectorAll('#qRows [data-q]').length===5,'练页一键只看五例');ok([...d.querySelectorAll('#qRows [data-q]')].map(e=>+e.dataset.q).join(',')===pilot.map(q=>q.n).join(','),'五例按解释递进排列，不重排原库');
for(let i=0;i<5;i++){
 click($('#qRows [data-q="'+pilot[i].n+'"]'));await wait(70);ok(!$('.case-reasoning'),'默认不提前展示推理');click($('#bJie'));ok($('#L2').textContent.length>30&&!$('.case-reasoning'),'原解仍先独立展示');click($('#bChai'));ok($('.case-reasoning').dataset.caseReasoning===pilot[i].id,'正确展开第'+(i+1)+'例');
 const loc=JSON.parse(JSON.stringify(w.YGN_HOOK.loc()));ok(loc.scr==='quiz'&&loc.id===pilot[i].n&&loc.layer==='chai','笔记位置保留命例和拆解层');
 ok($('#bNext').disabled===(i===4),'第五例停止，不能误跳到未补解命例');
 if(i===0){click($('#bNext'));await wait(70);ok(w.YGN_HOOK.loc().id===pilot[1].n,'下一题在五例内连续学习');w.YGN_HOOK.go(loc);await wait(70);ok(!!$('.case-reasoning')&&w.YGN_HOOK.loc().id===pilot[i].n,'笔记回出处自动展开对应拆解');}
 click($('#bList'));await wait(70);
}
click($('#btnSearch'));await wait(60);$('#q').value='把地支的胜利误算成了天干也已清场';$('#q').dispatchEvent(new w.Event('input',{bubbles:true}));await wait(1100);
const hit=d.querySelector('#hits .hit[data-h]');ok(!!hit,'AI新增推理可全文检索');click(hit);await wait(100);ok(!!$('.case-reasoning')&&$('#quizBody').textContent.includes('两处未交代'),'搜索自动展开推理层并定位命例');
ok(errors.length===0,'无脚本错误');ok(!Object.keys(w.localStorage).some(k=>/^bazi_/.test(k)),'学习记录仍使用盲派独立存储');console.log('通过',checks,'项五例拆解检查');dom.window.close();
})().catch(e=>{console.error(e);dom.window.close();process.exitCode=1});
