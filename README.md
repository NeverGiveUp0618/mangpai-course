# 盲派八字 · mangpai-course

仿「命理精讲」的盲派八字学习站：**学**（初/中/高级课程）、**查**（专题与答疑）、**练**（命例库，三层展开＋吸顶四柱盘）、搜索、我的笔记、阅读进度。
本地项目，**尚未发布**（资料版权来自段建业系，发布前先确认）。

## 流程
```
_src/txt/*.txt（原始资料提取文本，不进 git）
   └ python3 convert.py   → content/{初级,中级,高级,专题}/*.md + _src/cases.json + _src/books.json
        └ python3 build_mp.py → data/data-{meta,course,notes,quiz}.js
             └ NODE_PATH=../bazi-course/node_modules node smoke_mp.js
```
`_patch_app.py`：从 bazi-course 复制 app.js/index.html 并改成本站（存储键 `mp_course_*`，去掉入站自检、断命台、v课、复习卡）。

## 收录范围
- 收：成熟期（2006–2011）网授班辅导资料、初级整理版、大连面授、中级班讲义、高级班讲义、济南/盐城面授笔记、六亲班、专题问答。
- 不收：早期仍用用神的《命理珍宝》《授课教程》《263例》；纳音专文；含六爻/奇门的段落。
- 暂缺（二期）：4 份扫描 PDF（济南2010教材、干支奥义、职业象法新解、案例集）OCR 错字多；面授笔记里以图片给出的命盘。

## 二期待办
命例标题与主题归类优化、盘为图片的命例补录、扫描件校对后收录、断命台/复习卡/速查、题目化练习。
