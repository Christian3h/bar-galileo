#!/usr/bin/env python3
"""
Create a placeholder default image for the project.

This script will create a `default.jpg` file under the project's MEDIA folder:
  <repo-root>/bar_galileo/media/productos/default.jpg

Usage:
  python create_default_image.py            # create default.jpg with defaults
  python create_default_image.py --force    # overwrite if exists
  python create_default_image.py --width 800 --height 600 --text "No Image"

Notes:
- The script expects to live at the repository root next to the `bar_galileo/` Django package:
    repo/
      create_default_image.py   <-- this file
      bar_galileo/
        media/
- If Pillow is not installed the script prints instructions to install it.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    IMAGE_LIB_AVAILABLE = False
else:
    IMAGE_LIB_AVAILABLE = True


def get_target_path() -> Path:
    """
    Compute the destination path for the default image.

    We assume the repo layout has a `bar_galileo` package directory next to this script,
    and MEDIA_ROOT is `bar_galileo/media`. The placeholder will be saved to:
      bar_galileo/media/productos/default.jpg
    """
    here = Path(__file__).resolve().parent
    bar_pkg = here / "bar_galileo"
    # Fallback: if this script is executed from inside bar_galileo, adjust accordingly
    if not bar_pkg.exists():
        # try parent as repo root in edge cases
        candidate = here.parent / "bar_galileo"
        if candidate.exists():
            bar_pkg = candidate

    media_root = bar_pkg / "media"
    target_dir = media_root / "productos"
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / "default.jpg"


def create_placeholder_image(path: Path, width: int, height: int, text: str, force: bool) -> None:
    if path.exists() and not force:
        print(f"Default image already exists at: {path}")
        print("Use --force to overwrite.")
        return

    if not IMAGE_LIB_AVAILABLE:
        print("Pillow (PIL) is required to generate the image.")
        print("Install it with:")
        print("    pip install Pillow")
        raise SystemExit(2)

    # Colors
    bg_color = (240, 240, 240)  # light grey
    card_color = (230, 230, 230)
    accent_color = (200, 200, 200)
    icon_color = (160, 160, 160)
    text_color = (120, 120, 120)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw a central rounded card
    margin = int(min(width, height) * 0.07)
    card_box = [margin, margin, width - margin, height - margin]
    # Simple rounded rectangle: draw rectangle + circles in corners
    radius = int(min(width, height) * 0.03)
    try:
        # Pillow >= 5.0 supports rounded_rectangle
        draw.rounded_rectangle(card_box, radius=radius, fill=card_color)
    except Exception:
        # fallback: draw rectangle (no rounding)
        draw.rectangle(card_box, fill=card_color)

    # Draw a simple "photo" icon inside the card: a smaller rectangle with a mountain-like triangle
    inner_margin = int(min(width, height) * 0.12)
    photo_box = [card_box[0] + inner_margin, card_box[1] + inner_margin,
                 card_box[2] - inner_margin, card_box[1] + int((card_box[3] - card_box[1]) * 0.58)]
    draw.rectangle(photo_box, fill=accent_color)

    # Draw mountains: simple polygon(s)
    left = photo_box[0] + int((photo_box[2] - photo_box[0]) * 0.08)
    right = photo_box[2] - int((photo_box[2] - photo_box[0]) * 0.08)
    top = photo_box[1] + int((photo_box[3] - photo_box[1]) * 0.12)
    bottom = photo_box[3] - int((photo_box[3] - photo_box[1]) * 0.08)

    # first mountain
    m1 = [(left, bottom),
          (left + int((right - left) * 0.24), top + int((bottom - top) * 0.38)),
          (left + int((right - left) * 0.46), bottom)]
    draw.polygon(m1, fill=icon_color)

    # second (smaller) mountain overlapping
    m2 = [(left + int((right - left) * 0.38), bottom),
          (left + int((right - left) * 0.64), top + int((bottom - top) * 0.18)),
          (left + int((right - left) * 0.84), bottom)]
    draw.polygon(m2, fill=(220, 220, 220))

    # Draw a simple sun/circle
    sun_radius = int(min(width, height) * 0.03)
    sun_center = (photo_box[2] - sun_radius - int((photo_box[2] - photo_box[0]) * 0.06),
                  photo_box[1] + sun_radius + int((photo_box[3] - photo_box[1]) * 0.06))
    draw.ellipse([sun_center[0] - sun_radius, sun_center[1] - sun_radius,
                  sun_center[0] + sun_radius, sun_center[1] + sun_radius], fill=(255, 255, 255))

    # Draw the placeholder text centered below the photo_box
    # Try to load a truetype font; fall back to default if not available.
    font_size = max(12, int(min(width, height) * 0.035))
    font = None
    try:
        # Common system font paths may vary; try a few known options
        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
        for p in possible_fonts:
            if Path(p).exists():
                font = ImageFont.truetype(p, font_size)
                break
    except Exception:
        font = None

    if font is None:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

    text_to_draw = text.strip() if text and text.strip() else "NO IMAGE AVAILABLE"
    # center horizontally; place vertically below the photo_box with some padding
    if font:
        # Different Pillow versions expose different measurement helpers.
        # Prefer font.getbbox (modern), fall back to font.getsize, otherwise estimate.
        try:
            bbox = font.getbbox(text_to_draw)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except Exception:
            try:
                tw, th = font.getsize(text_to_draw)
            except Exception:
                # As a last resort, approximate width using character count and font size.
                tw = int(len(text_to_draw) * font_size * 0.6)
                th = font_size
    else:
        # No font available; approximate
        tw = int(len(text_to_draw) * font_size * 0.6)
        th = font_size
    text_x = (width - tw) // 2
    text_y = photo_box[3] + int((card_box[3] - photo_box[3]) * 0.12)
    # Draw shadow for better contrast
    shadow_offset = 1
    try:
        if font:
            draw.text((text_x + shadow_offset, text_y + shadow_offset), text_to_draw, fill=(255, 255, 255), font=font)
            draw.text((text_x, text_y), text_to_draw, fill=text_color, font=font)
        else:
            draw.text((text_x + shadow_offset, text_y + shadow_offset), text_to_draw, fill=(255, 255, 255))
            draw.text((text_x, text_y), text_to_draw, fill=text_color)
    except Exception:
        # As a fallback, draw without shadow
        if font:
            draw.text((text_x, text_y), text_to_draw, fill=text_color, font=font)
        else:
            draw.text((text_x, text_y), text_to_draw, fill=text_color)

    # Save as JPEG (default.jpg)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(path), "JPEG", quality=90)
        print(f"Created placeholder image at: {path}")
    except Exception as exc:
        print(f"Failed to save image to {path}: {exc}")
        raise


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Create a default placeholder image for products.")
    p.add_argument("--width", type=int, default=1200, help="Image width in pixels (default: 1200)")
    p.add_argument("--height", type=int, default=1600, help="Image height in pixels (default: 1600)")
    p.add_argument("--text", type=str, default="NO IMAGE AVAILABLE", help="Text to display on the placeholder")
    p.add_argument("--force", action="store_true", help="Overwrite existing default.jpg if present")
    p.add_argument("--show-path", action="store_true", help="Print the computed target path and exit")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    target = get_target_path()
    if args.show_path:
        print(str(target))
        return

    try:
        create_placeholder_image(target, args.width, args.height, args.text, args.force)
    except SystemExit:
        raise
    except Exception as exc:
        print("Error:", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()