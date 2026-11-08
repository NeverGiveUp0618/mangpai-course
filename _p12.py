p='smoke_mp.js'; s=open(p).read()
s=s.replace("'data/data-quiz.js'].forEach(run);","'data/data-quiz.js', 'data/data-raw.js'].forEach(run);",1)
s=s.replace("  console.log('专题');","""  const rawCard = $('.rawg [data-ch]');
  ok(!!rawCard, '有原稿讲义卡片');
  click(rawCard); await wait(250);
  ok($('#chapterBody').textContent.length > 1500, '原稿章节按需加载后有正文');
  click($('#btnBack')); await wait(50);

  console.log('专题');""",1)
open(p,'w').write(s)
