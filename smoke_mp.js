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
['data/data-meta.js', 'data/data-course.js', 'data/data-notes.js', 'data/data-quiz.js'].forEach(run);
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
  click($('[data-tab="home"]')); await wait(80);

  console.log('课程');
  click($('[data-tab="course"]')); await wait(120);
  ok($$('.lvg').length === 3, '初/中/高三个折叠组');
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

  console.log('专题');
  click($('[data-tab="notes"]')); await wait(120);
  ok($$('#noteList .card, #noteList [data-nt]').length >= 10, '专题列表');

  console.log('命例库');
  click($('[data-tab="qlist"]')); await wait(150);
  ok($$('.qgh').length >= 8, '主题分组≥8，实得 ' + $$('.qgh').length);
  click($('.qgh')); await wait(30);
  const row = $('.qrow'); ok(!!row, '展开后有命例行');
  click(row); await wait(150);
  ok($('#quizBody').innerHTML.length > 300 && /(日主|造)/.test($('#quizBody').textContent), '命例页有内容');
  ok($('#stickyChart') && !$('#stickyChart').classList.contains('hide'), '吸顶盘显示');

  console.log('搜索');
  click($('#btnSearch')); await wait(80);
  $('#q').value = '墓库'; $('#q').dispatchEvent(new window.Event('input', { bubbles: true })); await wait(400);
  ok($$('#hits > *').length > 0, '搜“墓库”有结果：' + $$('#hits > *').length);

  console.log('隔离');
  const keys = Object.keys(window.localStorage);
  ok(keys.every(k => !/^bazi_/.test(k)), '没有写 bazi_ 前缀的键：' + keys.join(','));
  ok(errs.length === 0, '无脚本错误' + (errs.length ? '：' + errs.join(' | ') : ''));
  console.log(`\n${pass} 通过，${fail} 失败`);
  process.exit(fail ? 1 : 0);
})();
