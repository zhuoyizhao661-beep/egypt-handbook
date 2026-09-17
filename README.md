# 在埃及，看懂千年 — 人文旅行杂志

一部单文件离线阅读版埃及随身手册。线上地址：

**https://zhuoyizhao661-beep.github.io/egypt-handbook/**

`index.html` 是**生成产物**，不要直接改它 —— 下次跑一次构建就会被覆盖。要改内容请改源文件，然后重新生成。

---

## 快速开始

```bash
git clone https://github.com/zhuoyizhao661-beep/egypt-handbook.git
cd egypt-handbook
python3 -m pip install pillow     # 唯一的依赖
./build.sh                        # 重新生成 index.html
open index.html                   # 本地预览
```

改完提交推送，Pages 会在 1~2 分钟内自动重建：

```bash
git add -A && git commit -m "补充第 X 章" && git push
```

---

## 改哪里

| 想改什么 | 改这个文件 |
| --- | --- |
| 正文文字、章节导语、图说、资料来源编号 | `work/illustrated/book.json` |
| 八个章节的标题、英文副题、章首导语 | `work/magazine/redesign.py` 顶部的 `chapters` 列表 |
| 配色、字体、排版、间距 | `work/magazine/magazine.css` |
| 阅读进度条、目录抽屉等交互 | `work/magazine/magazine.js` |
| 封面图 | `work/magazine/giza-hd.jpg`（直接换文件即可） |
| 某一张内文配图 | `python3 tools/set_photo.py`，见下 |

### 正文

`work/illustrated/book.json` 里是一个 `pages` 数组，每一项是一个页面：

```json
{
  "kind": "story",
  "key": "nut_story",          // 唯一标识，同时决定原图落在哪个 article 里
  "tag": "第五章",
  "title": "太阳以西，生命继续",
  "lead": "导语……",
  "sections": [ { "h": "小标题", "p": "正文段落" } ],
  "image": "nut",               // 用哪张图，见 tools/set_photo.py
  "caption": "图说",
  "note": "随手记……",
  "sources": "9、10、35"        // 对应卷末资料索引的编号
}
```

改完跑 `./build.sh`。**别动 `kind`、`key` 这两个字段** —— 布局和配图都靠它们对应。新增页面时复制一段现成的改就行，`key` 取个不重复的名字。

### 换配图

```bash
python3 tools/set_photo.py                    # 列出所有可换的图片 key
python3 tools/set_photo.py nut 我的照片.jpg    # 把 KV9 那张换掉
./build.sh
```

脚本会自动等比缩到最长边 1600、JPEG 质量 89，和原有处理方式一致，尺寸属性也会重新算。封面要用 `giza` 这个 key，脚本会写到 `giza-hd.jpg`（封面刻意不走 `original.html`）。

仓库里的 `work/illustrated/assets/` 是全部原图，`assets_meta.json` 记着每张图的作者、来源和许可协议。**如果换上新照片，记得把署名和许可信息补进卷末的图片署名里**，这册子用的多是 Wikimedia 上的 CC BY-SA 和公有领域图，署名是许可要求。

---

## 两个容易踩的坑

**1. 不要随便跑 `work/illustrated/content_v2.py`。** 它是更上游的整理脚本，会把 `work/pdf/content.json` 重新组装成 `book.json` —— 也就是**覆盖掉你手改的正文**。除非要整本重排，否则不用碰它。

**2. 卷末的「资料索引」和「图片署名」不在 `book.json` 里**，它们在 `work/magazine/original.html` 里被 `redesign.py` 按 `<article id="sources">` / `<article id="credits">` 抓取。那个文件 5MB（图片都是内嵌 base64），改起来比较费劲 —— 改文字用编辑器的查找替换只动那两段就好，别整体重排格式。

---

## 文件说明

```
index.html                        生成产物，线上就是这个文件
build.sh                          一键重新生成
tools/set_photo.py                换配图
work/magazine/redesign.py         生成器：结构、章节、卷末附录
work/magazine/magazine.css        样式
work/magazine/magazine.js         交互
work/magazine/original.html       上一版的完整 HTML，配图和数据来源
work/magazine/giza-hd.jpg         封面图
work/illustrated/book.json        正文内容
work/illustrated/content_v2.py    正文整理脚本（上游，慎跑）
work/illustrated/assets/          全部原图
work/illustrated/assets_meta.json 原图的作者、来源、许可
work/pdf/content.json             最初的内容草稿
```

`outputs/` 是构建中间产物，已被 `.gitignore` 忽略，不用提交。
