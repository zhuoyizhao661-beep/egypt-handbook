from pathlib import Path
import json,re,base64,html,hashlib,io
from PIL import Image
ROOT=Path.cwd(); W=ROOT/'work/magazine'; OUT=ROOT/'outputs/埃及随身手册·离线图文阅读版.html'
book=json.loads((ROOT/'work/illustrated/book.json').read_text()); pages=book['pages']; meta=json.loads((ROOT/'work/illustrated/assets_meta.json').read_text()); original=(W/'original.html').read_text()
e=html.escape
# Art direction: warm limestone paper, monumental serif typography, museum-dark image spreads.
# Sequence: photographic cover, editorial contents, eight chapters, retained references and credits.
# Motion: cover entrance, fine reading-progress line, sliding contents drawer; reduced-motion respected.
chapters=[
 ('timeline','序章','时间、诸神与来世','BEFORE THE JOURNEY','读懂一面墙，从认识它相信的世界开始。',None),
 ('gem','第一章','黄金之内，人的世界','THE GRAND EGYPTIAN MUSEUM','从一条船、一张王座，看见文明的日常与理想。','throne'),
 ('giza','第二章','石头与永恒','THE GIZA PLATEAU','金字塔的宏大，也藏在建造者的工作日志里。','giza'),
 ('temple','第三章','众神居住的城市','THE TEMPLES OF LUXOR','走过柱厅、祭坛与游行的道路，进入古人的秩序。','karnak'),
 ('hatshepsut','第四章','她把名字刻进山崖','HATSHEPSUT','王权的形象、远航的荣耀，以及被改写的记忆。','hatshepsut_temple'),
 ('west','第五章','太阳以西，生命继续','THE WEST BANK','国王的墓室之外，还有画出永生的工匠。','nut'),
 ('redsea','第六章','海底，另一种时间','THE RED SEA & SINAI','从古代航路到二战沉船，海水保存了不同的年代。','thistlegorm'),
 ('dahab','终章','在海岸，回到今天','DAHAB & LIVING EGYPT','遗址之外，还有语言、食物与正在生活的人。','dahab')]
starts={c[0]:i for i,c in enumerate(chapters)}
active=0; groups=[[] for c in chapters]
for p in pages[2:]:
 if p['key'] in starts:active=starts[p['key']]
 groups[active].append(p)
assets={}
for p in pages:
 k=p.get('image')
 if k:
  # Read the reviewed asset actually embedded in the earlier HTML.
  art=re.search(r'<article id="'+p['key']+r'">(.*?)</article>',original,re.S).group(1)
  assets[k]=re.search(r'<img src="([^"]+)"',art).group(1)
if (W/'giza-hd.jpg').exists():
 assets['giza']='data:image/jpeg;base64,'+base64.b64encode((W/'giza-hd.jpg').read_bytes()).decode()
dimensions={k:Image.open(io.BytesIO(base64.b64decode(v.split(',')[1]))).size for k,v in assets.items()}
def image(k,caption='',cls='',lazy=True):
 alt=caption or {'giza':'吉萨金字塔群','throne':'图坦卡蒙黄金王座','karnak':'卡纳克神庙柱厅','hatshepsut_temple':'哈特谢普苏特祭庙','nut':'帝王谷 KV9 墓室天顶','thistlegorm':'锡斯尔戈姆号沉船中的摩托车','dahab':'达哈卜海岸'}.get(k,meta[k]['title'])
 return f'<figure class="{cls}"><img src="{assets[k]}" width="{dimensions[k][0]}" height="{dimensions[k][1]}" alt="{e(alt)}" '+('loading="lazy" ' if lazy else 'fetchpriority="high" ')+f'decoding="async">'+(f'<figcaption>{e(caption)}</figcaption>' if caption else '')+'</figure>'
css=(W/'magazine.css').read_text(); js=(W/'magazine.js').read_text()
parts=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#24231f"><link rel="icon" href="data:,"><title>在埃及，看懂千年 — 人文旅行杂志</title><style>'+css+'</style></head><body>']
parts+=['<a class="skip" href="#contents">跳到目录</a><header class="reader-bar"><a class="wordmark" href="#cover">埃及<span>EGYPT</span></a><span class="current-chapter">人文旅行手册</span><button class="menu-button" type="button" aria-haspopup="dialog" aria-controls="contents-dialog"><span>目录</span><i aria-hidden="true"></i></button><div class="reading-progress" aria-hidden="true"></div></header>']
parts+=['<main><section id="cover" class="cover" aria-labelledby="cover-title">'+image('giza',cls='cover-image',lazy=False)+'<div class="cover-shade"></div><div class="cover-masthead"><span>文明的远行</span><span>A JOURNEY THROUGH TIME</span><span>VOL. 01 / EGYPT</span></div><div class="cover-copy"><p class="eyebrow">人文 · 历史 · 海岸</p><h1 id="cover-title">在埃及<br><span>看懂千年</span></h1><p class="cover-deck">让眼前的石头，<br>重新拥有名字与故事。</p></div><div class="cover-bottom"><a href="#contents" class="open-book">翻开手册 <span aria-hidden="true">↓</span></a><p>吉萨 · 卢克索 · 西奈<br>一部随身携带的文明读本</p></div><span class="cover-vertical" aria-hidden="true">THE NILE / THE DESERT / THE SEA</span></section>']
parts+=['<section id="contents" class="contents section-shell"><div class="section-heading"><p class="eyebrow">CONTENTS / 阅读这片土地</p><h2>风沙之外，<br>故事仍在。</h2><p class="intro">到了现场，先读一页导览。<br>想再多了解一点，就往下读一个故事。</p><span class="edition">八个篇章 · 从尼罗河到红海</span></div><nav class="contents-list" aria-label="篇章目录">']
for i,c in enumerate(chapters):parts.append(f'<a href="#chapter-{i}"><span class="index">{i+1:02d}</span><span><strong>{c[2]}</strong><small>{c[3]}</small></span><span class="nav-arrow" aria-hidden="true">↗</span></a>')
parts+=['</nav><p class="offline-note">全部照片与图示随册保存，可离线阅读。<a href="#sources">资料索引</a>与<a href="#credits">图片署名</a>见卷末。</p></section>']
folio=0
for i,(c,group) in enumerate(zip(chapters,groups)):
 key,label,title,en,deck,img=c
 parts.append(f'<section class="chapter" data-chapter="{e(title)}" aria-labelledby="chapter-title-{i}">')
 if img:
  parts.append(f'<div id="chapter-{i}" class="chapter-opener opener-{i}">'+image(img,cls='chapter-photo')+f'<div class="opener-shade"></div><div class="opener-copy"><p class="eyebrow">{label} / {en}</p><h2 id="chapter-title-{i}">{title}</h2><p>{deck}</p></div><span class="chapter-numeral" aria-hidden="true">{i+1:02d}</span></div>')
 else:
  parts.append(f'<div id="chapter-{i}" class="prelude section-shell"><span class="prelude-number" aria-hidden="true">01</span><div><p class="eyebrow">{label} / {en}</p><h2 id="chapter-title-{i}">{title}</h2><p>{deck}</p></div></div>')
 parts.append('<nav class="chapter-nav section-shell" aria-label="'+title+'篇内目录"><span>本章阅读</span>')
 for p in group:parts.append(f'<a href="#{p["key"]}">{e(p["title"])}</a>')
 parts.append('</nav>')
 for p in group:
  folio+=1;k=p['key']; dark=k in ['throne_story','nut_story','wreck_story']; panoramic=k in ['judgement','giza_story','dahab_story']; cls=('story' if p['kind']=='story' else 'guide')+(' has-photo' if p.get('image') else '')+(' dark-spread' if dark else '')+(' panoramic' if panoramic else '')
  parts.append(f'<article id="{k}" class="essay {cls}" aria-labelledby="title-{k}"><div class="essay-inner"><header class="essay-heading"><div class="kicker"><span>{e(p["tag"])} · '+('现场导览' if p['kind']=='guide' else '图文故事')+f'</span><span class="folio">{folio:02d}</span></div><h2 id="title-{k}">{e(p["title"])}</h2><p class="standfirst">{e(p["lead"])}</p></header><div class="essay-layout">')
  if p.get('image'):parts.append(image(p['image'],p['caption'],'story-image'))
  parts.append('<div class="essay-body">')
  if p.get('diagram'):
   art=re.search(r'<article id="'+k+r'">(.*?)</article>',original,re.S).group(1)
   svg=re.search(r'<svg.*?</svg>',art,re.S).group(0)
   for old,new in [('#287477','#9A7542'),('#183D3E','#322E27'),('#617270','#716B60'),('#E7EDE7','#E7E1D4'),('#E6EDE7','#E7E1D4'),('#b67d51','#9A7542')]:svg=svg.replace(old,new)
   svg=svg.replace('role="img"','role="img" aria-label="'+e(p['lead'])+'"')
   parts.append('<figure class="diagram">'+svg+'</figure>')
  parts.append('<div class="text-sections">')
  for j,(h,b) in enumerate(p['sections']):parts.append(f'<section class="text-section"><h3>{e(h)}</h3><p>{e(b).replace(chr(10),"<br>")}</p></section>')
  parts.append('</div>')
  if p.get('note'):parts.append('<aside class="field-note"><span>随手记</span><p>'+e(p['note'])+'</p></aside>')
  parts.append('</div></div><footer class="essay-footer">')
  if p.get('sources'):parts.append('<a href="#sources">资料索引 '+e(p['sources'])+'</a>')
  parts.append(f'<a href="#chapter-{i}">返回本章 <span aria-hidden="true">↑</span></a></footer></div></article>')
 parts.append('</section>')
# Retain every verified citation and photo attribution; collapse appendices to keep the reading rhythm.
for name,title in [('sources','资料索引'),('credits','图片署名')]:
 art=re.search(r'<article id="'+name+r'">(.*?)</article>',original,re.S).group(1)
 items=re.findall(r'<div class="source-item">.*?</div>',art,re.S)
 parts.append(f'<section id="{name}" class="appendix section-shell"><details><summary><span class="eyebrow">'+('SOURCES' if name=='sources' else 'PHOTOGRAPHY')+f'</span><h2>{title}</h2><span class="details-mark" aria-hidden="true">+</span></summary><div class="appendix-body">')
 if name=='sources':parts.append('<p>正文已提炼中文要点。以下资料留作延伸阅读与核对。</p>')
 parts.extend(items)
 if name=='credits':parts.append('<p class="credit-note">文物与遗址照片来自原署名作者。封面与章首页作局部取景，图说页保留完整原图；未改变照片内容。图示为本册绘制的关系与空间示意，不替代考古测绘、现场指引或潜水计划。展陈与开放情况以馆方及现场为准。</p>')
 parts.append('</div></details></section>')
parts.append('<footer class="colophon section-shell"><p class="eyebrow">THE JOURNEY CONTINUES</p><h2>带着故事，<br>再看一眼埃及。</h2><a href="#cover">回到封面 ↑</a><div><span>在埃及，看懂千年</span><span>人文旅行手册 / 2026.09</span></div></footer></main>')
parts.append('<dialog id="contents-dialog" aria-labelledby="drawer-title"><div class="drawer-head"><p class="eyebrow">THE FIELD COMPANION</p><button class="close-menu" type="button" aria-label="关闭目录">关闭 <span aria-hidden="true">×</span></button></div><h2 id="drawer-title">去往哪一章？</h2><nav class="drawer-links" aria-label="快捷篇章目录">')
for i,c in enumerate(chapters):parts.append(f'<a href="#chapter-{i}"><span>{i+1:02d}</span>{c[2]}<i aria-hidden="true">↗</i></a>')
parts.append('<a href="#quick"><span>查阅</span>每站带走一句话<i aria-hidden="true">↗</i></a></nav><p class="drawer-note">一页导览，认出遗址。<br>几个故事，理解它为什么存在。</p></dialog><script>'+js+'</script></body></html>')
OUT.write_text(''.join(parts))
(W/'manifest.json').write_text(json.dumps({'html':str(OUT),'chapters':len(chapters),'articles':folio,'photos':14,'size':OUT.stat().st_size},ensure_ascii=False,indent=2))
print((W/'manifest.json').read_text())
