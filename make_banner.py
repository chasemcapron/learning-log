"""Render assets/banner.svg (LEARNING LOG in the pixel-block style). Needs gen_header.py from the profile repo."""
import sys, pathlib
here = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent))
from gen_header import pixel_svg
svg, w, h = pixel_svg(["LEARNING LOG"], cursor=True, CELL=10)
(here / "assets" / "banner.svg").write_text(svg, encoding="utf-8")
print(f"wrote assets/banner.svg ({w}x{h})")
