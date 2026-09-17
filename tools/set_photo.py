#!/usr/bin/env python3
"""换掉某一处配图。

用法（在仓库根目录执行）：
    python3 tools/set_photo.py <图片key> <新照片路径>
    python3 tools/set_photo.py            # 列出全部可用的 key

例：
    python3 tools/set_photo.py nut ~/Downloads/我的KV9照片.jpg
    ./build.sh          # 重新生成 index.html

原理：配图是 base64 内嵌在 work/magazine/original.html 里的。这个脚本会按
book.json 里记录的关系，找到该图片所在的 <article>，把它第一张图换成新照片
（等比缩到最长边 1600、JPEG 质量 89，和原来的处理方式一致），尺寸属性由
redesign.py 自动重新计算，不用手动改。
"""

import base64
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = ROOT / "work/magazine/original.html"
BOOK = ROOT / "work/illustrated/book.json"
COVER = ROOT / "work/magazine/giza-hd.jpg"

MAX_EDGE = 1600
QUALITY = 89


def image_owners():
    """图片 key -> 提供该图的 article id（取第一个用到它的页面）。"""
    pages = json.loads(BOOK.read_text(encoding="utf-8"))["pages"]
    owners = {}
    for p in pages:
        k = p.get("image")
        if k and k not in owners:
            owners[k] = p["key"]
    return owners


def encode(path):
    from PIL import Image

    im = Image.open(path)
    im.load()
    im = im.convert("RGB")
    im.thumbnail((MAX_EDGE, MAX_EDGE))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=QUALITY)
    return buf.getvalue(), im.size


def main():
    owners = image_owners()

    if len(sys.argv) != 3:
        print(__doc__)
        print("可用的图片 key：")
        for k, v in owners.items():
            mark = "（封面，见下方说明）" if k == "giza" else ""
            print(f"  {k:20s} 当前取自 {v}{mark}")
        sys.exit(0 if len(sys.argv) == 1 else 2)

    key, src = sys.argv[1], Path(sys.argv[2]).expanduser()
    if key not in owners:
        sys.exit(f"没有这个图片 key：{key}\n可用：{', '.join(owners)}")
    if not src.is_file():
        sys.exit(f"找不到照片：{src}")

    raw, size = encode(src)

    # 封面（giza）在 redesign.py 里被 giza-hd.jpg 覆盖，所以要改的是那个文件。
    if key == "giza":
        COVER.write_bytes(raw)
        print(f"封面已替换：{COVER.relative_to(ROOT)}  {size[0]}×{size[1]}  {len(raw):,} 字节")
        print("提示：封面走的是 giza-hd.jpg，不是 original.html，这是刻意的。")
        return

    article = owners[key]
    html = ORIGINAL.read_text(encoding="utf-8")
    m = re.search(r'<article id="' + re.escape(article) + r'">(.*?)</article>', html, re.S)
    if not m:
        sys.exit(f"在 original.html 里找不到 <article id=\"{article}\">")

    body = m.group(1)
    img = re.search(r'<img src="data:image/jpeg;base64,[^"]*"', body)
    if not img:
        sys.exit(f'<article id="{article}"> 里没有内嵌图片')

    new_src = 'src="data:image/jpeg;base64,' + base64.b64encode(raw).decode() + '"'
    new_body = body[: img.start()] + '<img ' + new_src + body[img.end() :]
    ORIGINAL.write_text(html[: m.start(1)] + new_body + html[m.end(1) :], encoding="utf-8")

    print(f"已替换 {key}（article={article}）：{size[0]}×{size[1]}，{len(raw):,} 字节")
    print("接着跑 ./build.sh 重新生成 index.html")


if __name__ == "__main__":
    main()
