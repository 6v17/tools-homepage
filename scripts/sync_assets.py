#!/usr/bin/env python3
"""Sync VideoSeek screenshots, build WebP variants, and regenerate share image."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CANDIDATES = [
    Path(r"D:\PycharmProjects\VideoSeek\docs\assets"),
    Path(r"C:\Users\LiuWei\PycharmProjects\VideoSeek\docs\assets"),
    ROOT.parent / "VideoSeek" / "docs" / "assets",
]
SCREENSHOTS = ROOT / "img" / "screenshots"
ICON = ROOT / "img" / "icons" / "video-seek.ico"
SHARE_IMAGE = ROOT / "img" / "og-share.png"
MAX_PNG_BYTES = 240 * 1024
MAX_PNG_WIDTH = 1200
MIN_PNG_WIDTH = 840

MAPPING = {
    "image-search.png": ("\u56fe", "\u641c"),
    "text-search.png": ("\u6587", "\u641c"),
    "understanding.png": ("\u89c6\u9891\u7406\u89e3",),
}


def match_source(name: str, markers: tuple[str, ...]) -> bool:
    return all(marker in name for marker in markers)


def resolve_source_dir() -> Path | None:
    for candidate in SOURCE_CANDIDATES:
        if candidate.is_dir():
            return candidate
    return None


def sync_screenshots() -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    source_dir = resolve_source_dir()
    if source_dir is None:
        print("skip sync: VideoSeek docs/assets not found")
        return

    for target, markers in MAPPING.items():
        source = next(
            (source_dir / name for name in os.listdir(source_dir) if match_source(name, markers)),
            None,
        )
        if source is None:
            raise FileNotFoundError(f"no source screenshot for {target}")
        shutil.copy2(source, SCREENSHOTS / target)
        print(f"synced {target} <- {source.name}")


def optimize_png(png: Path) -> None:
    image = Image.open(png).convert("RGB")
    width = min(image.width, MAX_PNG_WIDTH)
    while width >= MIN_PNG_WIDTH:
        resized = image.resize(
            (width, max(1, int(image.height * width / image.width))),
            Image.Resampling.LANCZOS,
        )
        resized.save(png, format="PNG", optimize=True, compress_level=9)
        size_kb = png.stat().st_size // 1024
        if png.stat().st_size <= MAX_PNG_BYTES:
            print(f"png {png.name}: {size_kb}KB @ {width}px")
            return
        width -= 60
    print(f"png {png.name}: {png.stat().st_size // 1024}KB (still above target)")


def build_webp() -> None:
    for png in SCREENSHOTS.glob("*.png"):
        optimize_png(png)
        before = png.stat().st_size
        image = Image.open(png).convert("RGB")
        webp = png.with_suffix(".webp")
        image.save(webp, format="WEBP", quality=82, method=6)
        print(
            f"webp {webp.name}: {before // 1024}KB png -> {webp.stat().st_size // 1024}KB webp"
        )


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\msyhbd.ttc" if bold else r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoui.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def build_share_image() -> None:
    width, height = 1200, 630
    image = Image.new("RGB", (width, height), "#f4efe7")
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = (
            int(244 + (216 - 244) * ratio),
            int(239 + (228 - 239) * ratio),
            int(231 + (242 - 231) * ratio),
        )
        draw.line([(0, y), (width, y)], fill=color)

    draw.rounded_rectangle((56, 56, width - 56, height - 56), radius=36, fill=(255, 253, 249), outline=(15, 118, 110, 40), width=2)

    icon_size = 96
    if ICON.exists():
        icon = Image.open(ICON).convert("RGBA").resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        image.paste(icon, (96, 118), icon)

    title_font = load_font(64, bold=True)
    body_font = load_font(34)
    small_font = load_font(28)

    draw.text((220, 120), "VideoSeek", fill="#115e59", font=title_font)
    draw.text((96, 240), "用文字或截图，在本地素材库里找片段", fill="#1c2430", font=body_font)
    draw.text((96, 310), "索引与检索全部在本机完成，不上传你的视频", fill="#5f6877", font=small_font)

    chips = ["Windows 本地工具", "文字 / 图片搜索", "预览导出 MP4", "开源 AGPL-3.0"]
    x = 96
    y = 390
    for chip in chips:
        bbox = draw.textbbox((0, 0), chip, font=small_font)
        chip_w = bbox[2] - bbox[0]
        chip_h = bbox[3] - bbox[1]
        draw.rounded_rectangle((x, y, x + chip_w + 36, y + chip_h + 24), radius=999, fill="#e2f3f0")
        draw.text((x + 18, y + 10), chip, fill="#115e59", font=small_font)
        x += chip_w + 52

    SHARE_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    image.save(SHARE_IMAGE, format="PNG", optimize=True)
    print(f"share image -> {SHARE_IMAGE}")


def main() -> None:
    sync_screenshots()
    build_webp()
    build_share_image()


if __name__ == "__main__":
    main()
