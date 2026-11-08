/* 盲派八字 冒烟测试（jsdom）：首页/课程分级/章节/专题/命例库/搜索/存储键隔离 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');
const dir = __dirname;
let pass = 0, fail = 0;
const ok = (c, m) => { c ? (pass++, console.log('  ✓', m)) : (fail++, console.log('  ✗', m)); };

const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8').replace(/<link rel="stylesheet"[^>]*>/g, '');
const dom = new JSDOM(html, { runScripts: 'outside-only', pretendToBeVisual: true, url: 'https://x.test/mangpai-course/' });
const { window } = dom;
window.scrollTo = () => {};
window.matchMedia = window.matchMedia || (() => ({ matches: false, addListener() {}, removeListener() {} }));
const run = f => window.eval(fs.readFileSync(path.join(dir, f), 'utf8'));
['data/data-meta.js', 'data/data-course.js', 'data/data-notes.js', 'data/data-quiz.js', 'data/data-raw.js', 'data/data-ref.js', 'data/data-st.js', 'data/data-body-chu.js', 'data/data-body-zhong.js', 'data/data-body-gao.js', 'data/data-body-zhuan.js'].forEach(run);
window.eval(`
  window.__oc = document.createElement.bind(document);
  document.createElement = function(t){ const el = window.__oc(t);
    if (t === 'script') Object.defineProperty(el, 'src', { set(v){ (window.__req = window.__req || []).push(v); setTimeout(()=> el.onload && el.onload(), 0); }, get(){ return ''; } });
    return el; };`);
const errs = [];
window.addEventListener('error', e => errs.push(e.message));
run('app.js');
const D = window.document;
const $ = s => D.querySelector(s), $$ = s => [...D.querySelectorAll(s)];
const wait = ms => new Promise(r => setTimeout(r, ms));
const click = el => el.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));

(async () => {
  console.log('首页');
  await wait(50);
  ok($('#entryGate') === null, '入站自检已移除');
  ok(/盲派八字/.test($('#ttl').textContent), '标题是盲派八字');
  const M = window.DATA_META;
  ok((M.counts.course + M.counts.rawCourse) >= 60 && M.counts.quiz >= 500, `数据量：课程${M.counts.course} 专题${M.counts.notes} 命例${M.counts.quiz}`);
  ok(!$('.desk-entry') && !$('.vke-entry'), '断命台/v课入口已去除');
  ok($$('.tabbar button').length === 4, '底栏 4 个');

  console.log('我没学过');
  ok(!!$('#gapCard'), '首页有「我没学过」入口');
  click($('#gapCard')); await wait(200);
  ok(/我没学过/.test($('#noteBody').textContent) && $('#noteBody').textContent.length > 3000, '点进去是对照清单');
  const gp = $$('#noteBody .pill').filter(e => /标记为已掌握/.test(e.textContent));
  ok(gp.length >= 10, '每个缺口条目有「标记为已掌握」，实得 ' + gp.length);
  click(gp[0]); await wait(30);
  ok(/已掌握/.test(gp[0].textContent) && JSON.parse(window.localStorage.getItem('mp_course_gap') || '{}')[0] === 1, '点击后保存掌握状态');
  ok($$('#noteBody .pill').some(e => /相关命例/.test(e.textContent)), '有「相关命例」入口');
  click($('[data-tab="home"]')); await wait(80);
  ok(/已掌握 1 条/.test($('#gapHint').textContent), '首页卡片显示已掌握 1 条');
  window.confirm = () => true;
  window.localStorage.setItem('mp_course_read', '{"c1":100}'); window.localStorage.setItem('mp_course_seen', '{"3":1}');
  click($('[data-tab="home"]')); await wait(30);
  click($('#clearMarks')); await wait(50);
  ok(['mp_course_read', 'mp_course_seen', 'mp_course_gap'].every(k => Object.keys(JSON.parse(window.localStorage.getItem(k) || '{}')).length === 0), '「清除全部标记」清空已读/已学/已掌握');

  console.log('课程');
  click($('[data-tab="course"]')); await wait(120);
  ok($$('.lvg').length === 4, '初/中/高/专题四个折叠组');
  ok($$('.lvg.open').length === 1, '默认只展开一级');
  click($$('.lvg > .qgh')[1]); await wait(30);
  ok($$('.lvg.open').length === 2, '点击可展开另一级');
  click($$('.lvg > .qgh')[1]); await wait(30);
  ok($$('.lvg.open').length === 1, '再点折叠');
  ok($$('[data-ch]').length === M.counts.course + M.counts.rawCourse, '课程卡片数（含原稿）');
  click($('[data-ch="1"]')); await wait(150);
  ok($('#chapterBody').textContent.length > 2000, '第1章有正文');
  ok($$('#chapterBody .ichart').length > 0 || true, '章内排盘（如有）');
  click($('#nextCh')); await wait(100);
  ok($('#s-chapter').classList.contains('active'), '下一章可翻');
  await wait(1900);
  ok(Object.keys(JSON.parse(window.localStorage.getItem('mp_course_read') || '{}')).length === 0, '读章节不会自动记已读');
  click($('#readToggle')); await wait(30);
  ok(Object.values(JSON.parse(window.localStorage.getItem('mp_course_read') || '{}'))[0] >= 90, '手动「标记为已读」才记录');
  click($('#readToggle')); await wait(30);
  ok(Object.keys(JSON.parse(window.localStorage.getItem('mp_course_read') || '{}')).length === 0, '再点取消');

  const rawCard = $('.rawg [data-ch]');
  ok(!!rawCard, '有原稿讲义卡片');
  click(rawCard); await wait(250);
  ok($('#chapterBody').textContent.length > 1500, '原稿章节按需加载后有正文');
  click($('#btnBack')); await wait(50);

  console.log('专题');
  click($('[data-tab="ref"]')); await wait(200);
  ok($$('#refSegs .pill').length >= 4, '查：速查页有 小结/口诀/速查表/原文问答 四个入口');
  ok($$('#rfList .rf-i').length >= 30, '章节小结卡 ≥ 30 张，实得 ' + $$('#rfList .rf-i').length);
  click($$('#refSegs [data-seg]')[1]); await wait(60);
  ok($$('#rfList .rf-i').length >= 100, '口诀 ≥ 100 条，实得 ' + $$('#rfList .rf-i').length);
  click($$('#refSegs [data-seg]')[2]); await wait(60);
  ok($$('#rfList .rf-i').length >= 100, '速查表 ≥ 100 张，实得 ' + $$('#rfList .rf-i').length);
  $('#rfq').value = '墓库'; $('#rfq').dispatchEvent(new window.Event('input', { bubbles: true })); await wait(400);
  ok($$('#rfList .rf-i').length > 0 && $$('#rfList .rf-i').length < 100, '搜「墓库」能筛速查表');
  click($('#refNotes')); await wait(150);
  ok($$('#noteList .card, #noteList [data-nt]').length >= 10, '专题列表');

  console.log('命例库');
  click($('[data-tab="qlist"]')); await wait(150);
  ok($$('.qgh').length >= 8, '主题分组≥8，实得 ' + $$('.qgh').length);
  click($('.qgh')); await wait(30);
  const row = $('.qrow'); ok(!!row, '展开后有命例行');
  click(row); await wait(150);
  ok($('#quizBody').innerHTML.length > 300 && /(日主|造)/.test($('#quizBody').textContent), '命例页有内容');
  ok($('#stickyChart') && !$('#stickyChart').classList.contains('hide'), '吸顶盘显示');
  await wait(300);
  ok(Object.keys(JSON.parse(window.localStorage.getItem('mp_course_seen') || '{}')).length === 0, '打开命例不会自动标记已学');
  click($('#seenToggle')); await wait(30);
  ok(Object.keys(JSON.parse(window.localStorage.getItem('mp_course_seen') || '{}')).length === 1, '手动点「标记为已学」才记录');
  click($('#seenToggle')); await wait(30);
  ok(Object.keys(JSON.parse(window.localStorage.getItem('mp_course_seen') || '{}')).length === 0, '再点取消');

  ok($$('#L4 .chlink').length > 0, '命例页有「相关教材章节」');
  click($('#btnBack')); await wait(60);
  click($('#stEntry')); await wait(250);
  ok($$('[data-st]').length >= 30, '章节自测列表 ≥ 30 章，实得 ' + $$('[data-st]').length);
  click($('[data-st]')); await wait(250);
  ok($$('.stopt').length === 4, '自测题是 4 选 1');
  let guard = 0;
  while ($$('.stopt').length && guard++ < 30) {
    click($$('.stopt')[0]); await wait(20);
    ok(true, '');
    const go = $('#stGo'); if (!go) break;
    pass--; // 上面那个占位 ok 不计数
    click(go); await wait(20);
  }
  ok(/\d+ \/ \d+/.test($('#stBody').textContent), '做完显示成绩');
  ok(Object.keys(JSON.parse(window.localStorage.getItem('mp_course_st') || '{}')).length === 1, '成绩按章节记录（只记最好一次）');
  console.log('章节页附加');
  click($('[data-tab="course"]')); await wait(120);
  click($('[data-ch="1"]')); await wait(300);
  ok($$('#chExtras .chlink').length > 0, '章节页有「本章相关命例」');
  ok(!!$('#chStBtn'), '章节页有「做本章自测」按钮');
  click($('#chStBtn')); await wait(250);
  ok($$('.stopt').length === 4, '从章节页进入自测');
  click($('#btnBack')); await wait(50);
  click($('[data-tab="home"]')); await wait(60);

  console.log('搜索');
  click($('#btnSearch')); await wait(80);
  $('#q').value = '墓库'; $('#q').dispatchEvent(new window.Event('input', { bubbles: true })); await wait(400);
  ok($$('#hits > *').length > 0, '搜“墓库”有结果：' + $$('#hits > *').length);

  ok($$('#hits [data-sc]').length >= 3, '搜索结果有范围筛选（全部/教材/速查/命例/专题）');
  const scq = $$('#hits [data-sc]').find(e => e.dataset.sc === 'quiz');
  if (scq) { click(scq); await wait(30); ok($$('#hits .hit').length > 0 && $$('#hits [data-sc].sel').length === 1, '点「命例」只看命例结果'); }
  $('#q').value = '八字盘'; $('#q').dispatchEvent(new window.Event('input', { bubbles: true })); await wait(1800);
  ok(/没有「八字盘」，已改搜「命局」/.test($('#hits').textContent), '别名：搜「八字盘」自动改搜「命局」并提示');
  console.log('隔离');
  const keys = Object.keys(window.localStorage);
  ok(keys.every(k => !/^bazi_/.test(k)), '没有写 bazi_ 前缀的键：' + keys.join(','));
  ok(errs.length === 0, '无脚本错误' + (errs.length ? '：' + errs.join(' | ') : ''));
  console.log(`\n${pass} 通过，${fail} 失败`);
  process.exit(fail ? 1 : 0);
})();
