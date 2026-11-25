/* Approved case-reasoning batches: preserve originals, reachability, navigation, notes, search. */
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto'),{JSDOM}=require('jsdom');
let checks=0;const ok=(v,m)=>{assert(v,m);checks++;console.log('✓',m)},sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const sandbox={window:{}};vm.runInNewContext(fs.readFileSync('data/data-quiz.js','utf8'),sandbox);const Q=sandbox.window.DATA_QUIZ,qs=Q.items,manifest=JSON.parse(fs.readFileSync('content/命例拆解/目录.json')),approved=JSON.parse(fs.readFileSync('content/命例拆解/批次.json'));
ok(qs.length===936&&manifest.length===425&&approved.approvedTotal===425,'再增100后总425拆解，原命例936不增加不重排');
const original=qs.map(q=>{const c={...q};delete c.reasoningOrder;delete c.reasoningTitle;c.chai=c.chai.split('<hr><section class="case-reasoning"')[0];return c;});
ok(sha(JSON.stringify(original))==='f019609c13cfecb31e2590f22977d464ebdfb74549cbf150c22deedacdaa30ca','936命例原断原解/ID/盘/大运/关联/基础拆解整体不变');
const firstHashes=['a513577303050edc8b2d6919581a020e897e4f79c0bd8a4d600695275a4d6748','cc2a0bfa9135ca4c619971494a62bac6a8fda900992819e2a66c8c41e12c6a76','1c58da1cf993a22b5bf352b78b3c1bee3c0cea3ea5f769e0d6d972a30d52b9ac','78c0e221fa3b2d5b8f912a61471fa995969f6f711242c2e6d71b226010f80808','acfde514ca0e8914145861390057f47e770aa3172b9c3e4ccffcaf61bfacc379'];
ok(manifest.slice(0,5).every((r,i)=>sha(fs.readFileSync('content/命例拆解/'+r.file))===firstHashes[i]),'用户认可的原五篇逐字保持');
ok(sha(JSON.stringify(manifest.slice(0,105)))==='1896693dc00f6d87ed4e14bf83a38032ce3e3e02f73881d95bb1c4c5c8b30ae2','旧105条目录与证据原样保持');
const previous=JSON.parse(fs.readFileSync('reviews/case-reasoning-20261125.json'));
ok(previous.items.length===100&&previous.items.every(r=>sha(fs.readFileSync('content/命例拆解/'+r.file))===r.sha256),'上一批100篇逐字保持');
ok(sha(JSON.stringify(manifest.slice(0,125)))==='19b1ab3ad9c1c4d8c51b7a464cbd474fa60ad987617efa416cbec7d554d15d38','旧125条目录和证据保持');
const previous20=JSON.parse(fs.readFileSync('reviews/case-reasoning-20-20261125.json'));
ok(previous20.items.length===20&&previous20.items.every(r=>sha(fs.readFileSync('content/命例拆解/'+r.file))===r.sha256),'上一批20篇逐字保持');
ok(sha(JSON.stringify(manifest.slice(0,225)))==='dce309a722016cf218d2893ba90e1dbac3d26ba212d83134bf4d4453141424a6','旧225条目录和证据保持');
const previousNext100=JSON.parse(fs.readFileSync('reviews/case-reasoning-next100-20261125.json'));
ok(previousNext100.items.length===100&&previousNext100.items.every(r=>sha(fs.readFileSync('content/命例拆解/'+r.file))===r.sha256),'上一批126—225全部逐字保持');
ok(sha(JSON.stringify(manifest.slice(0,325)))==='ada755ef7191f5ecb83b81c8ad54e680fd37b6e9f9700483b7c999f4e93453fb','旧325条目录和证据保持');
const previous325=JSON.parse(fs.readFileSync('reviews/case-reasoning-325-20261125.json'));
ok(previous325.items.length===100&&previous325.items.every(r=>sha(fs.readFileSync('content/命例拆解/'+r.file))===r.sha256),'上一批226—325全部逐字保持');
const all=qs.filter(q=>q.reasoningOrder).sort((a,b)=>a.reasoningOrder-b.reasoningOrder),latest=all.filter(q=>approved.batches.at(-1).caseIds.includes(q.id));
ok(all.length===425&&latest.length===100&&all.map(q=>q.id).join('|')===manifest.map(r=>r.caseId).join('|'),'授权集合及425稳定ID与顺序一致');
ok(Q.reasoningBatches.length===6&&Q.reasoningBatches.at(-1).count===100,'新旧批次独立记录');
ok(all.every(q=>q.chai.includes('class="case-reasoning"')&&q.chai.includes('推断')&&q.chai.includes('核对依据短句')),'425例都有实质推理层、推断标识与来源核对');
ok(latest.every(q=>!q.chai.split('<details class="reasoning-evidence">')[1].includes('**')),'新短据不显示原Markdown加粗符号');
const dom=new JSDOM(fs.readFileSync('index.html','utf8').replace(/<link rel="stylesheet"[^>]*>/g,''),{url:'https://x.test/mangpai-course/',runScripts:'outside-only',pretendToBeVisual:true});const w=dom.window,d=w.document,errors=[];w.scrollTo=()=>{};w.matchMedia=()=>({matches:false,addListener(){},removeListener(){}});w.addEventListener('error',e=>errors.push(e.message));
for(const file of ['data-meta','data-course','data-notes','data-quiz','data-raw','data-ref','data-st','data-qna','data-plain','data-body-chu','data-body-zhong','data-body-gao','data-body-zhuan'])w.eval(fs.readFileSync('data/'+file+'.js','utf8'));
w.eval(`window.__create=document.createElement.bind(document);document.createElement=function(t){let e=window.__create(t);if(t==='script')Object.defineProperty(e,'src',{set(v){setTimeout(()=>e.onload&&e.onload(),0)}});return e;}`);w.eval(fs.readFileSync('app.js','utf8'));
const wait=ms=>new Promise(r=>setTimeout(r,ms)),click=e=>{assert(e,'missing element');e.dispatchEvent(new w.MouseEvent('click',{bubbles:true}))},$=s=>d.querySelector(s);
(async()=>{
await wait(50);w.YGN_HOOK.go({scr:'qlist',id:null});await wait(50);click($('[data-m="reasoning"]'));await wait(20);
ok(d.querySelectorAll('#qRows [data-q]').length===425,'全部425例可单独筛选');
click($('[data-m="reasoning-new"]'));await wait(20);ok(d.querySelectorAll('#qRows [data-q]').length===100,'本次新增100例一键可达');
ok([...d.querySelectorAll('#qRows [data-q]')].map(e=>+e.dataset.q).join(',')===latest.map(q=>q.n).join(','),'新增批次顺序正确，保留原命例编号');
for(let i=0;i<all.length;i++){
 const q=all[i];w.YGN_HOOK.go({scr:'quiz',id:q.n});await wait(0);ok(!$('.case-reasoning'),'命例'+q.n+'默认不提前显示AI推理');click($('#bJie'));ok($('#L2').textContent.length>30&&!$('.case-reasoning'),'命例'+q.n+'原解先独立展示');click($('#bChai'));ok($('.case-reasoning').dataset.caseReasoning===q.id,'第'+(i+1)+'篇正确挂到固定命例');
 const loc=w.YGN_HOOK.loc();ok(loc.scr==='quiz'&&loc.id===q.n&&loc.layer==='chai','第'+(i+1)+'篇笔记位置可返回展开层');
}
// Latest-only navigation must not drop into an unexpanded original case.
w.YGN_HOOK.go({scr:'qlist',id:null});await wait(10);click($('[data-m="reasoning-new"]'));await wait(10);click($('#qRows [data-q="'+latest[0].n+'"]'));await wait(10);ok($('#bPrev').disabled,'新增首例上一例边界');click($('#bNext'));await wait(10);ok(w.YGN_HOOK.loc().id===latest[1].n,'新增批次内下一例连续');
w.YGN_HOOK.go({scr:'quiz',id:latest.at(-1).n});await wait(10);ok($('#bNext').disabled,'第100新增例到此停止');
w.YGN_HOOK.go({scr:'quiz',id:all[0].n,layer:'chai'});await wait(10);ok($('#bPrev').disabled,'新增筛选下回看首批笔记，自动采用完整拆解序列');click($('#bNext'));await wait(10);ok(w.YGN_HOOK.loc().id===all[1].n,'首批笔记返回后的翻页仍在AI拆解序列');
w.YGN_HOOK.go({scr:'qlist',id:null});await wait(10);click($('[data-m="reasoning"]'));await wait(10);w.YGN_HOOK.go({scr:'quiz',id:all.at(-1).n});await wait(10);ok($('#bNext').disabled,'完整425例末尾停止');
const target=latest[0],loc={scr:'quiz',id:target.n,layer:'chai'};w.YGN_HOOK.go(loc);await wait(10);ok($('.case-reasoning').dataset.caseReasoning===target.id,'笔记回出处自动展开对应推理');w.YGN_HOOK.go(loc);await wait(10);ok(!!$('.case-reasoning'),'同一命例的出处返回也可展开');
click($('#btnSearch'));await wait(30);$('#q').value=target.reasoningTitle;$('#q').dispatchEvent(new w.Event('input',{bubbles:true}));await wait(1100);
const hit=$('#hits .hit[data-h]');ok(!!hit,'新增文章的推理标题可全文搜索');click(hit);await wait(30);ok($('.case-reasoning')?.dataset.caseReasoning===target.id,'搜索进入正确新例并展开推理层');
ok(errors.length===0,'无脚本异常');ok(!Object.keys(w.localStorage).some(k=>/^bazi_/.test(k)),'仍只写盲派记录，不串命理精讲');
console.log('通过',checks,'项批次、425例及回查检查');dom.window.close();
})().catch(e=>{console.error(e);dom.window.close();process.exitCode=1});
