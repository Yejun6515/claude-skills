"""pdf_read.py - read a PDF without poppler/pdftoppm.

Why: the Read tool's PDF path needs pdftoppm (poppler-utils), which is not installed
on this PC and needs admin rights. PyMuPDF is already installed and renders pages by
itself, so this covers both cases:

  * text PDFs  -> extract the text directly (cheap, no image tokens)
  * drawings / scans / CJK images -> render pages to PNG, then Read the PNG

Usage
  python pdf_read.py <file.pdf>                     # info + text of every page
  python pdf_read.py <file.pdf> --pages 1-3         # only those pages (1-based)
  python pdf_read.py <file.pdf> --png <outdir>      # render pages to PNG too
  python pdf_read.py <file.pdf> --png <outdir> --dpi 200 --only-images
                                                    # render only pages with no text layer
Output is UTF-8; PNG paths are printed so they can be opened with the Read tool.
"""
import argparse
import os
import sys

import fitz  # PyMuPDF

# stdout must be UTF-8 or Japanese/Korean text dies on the Windows console codepage
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TEXT_THRESHOLD = 40  # chars below this -> treat the page as image-only


def parse_pages(spec, count):
    if not spec:
        return list(range(count))
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a) - 1, int(b)))
        else:
            out.append(int(part) - 1)
    return [p for p in out if 0 <= p < count]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--pages", default="")
    ap.add_argument("--png", default="")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--only-images", action="store_true",
                    help="render only the pages that have no usable text layer")
    ap.add_argument("--max-chars", type=int, default=4000, help="per-page text cap")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    pages = parse_pages(args.pages, doc.page_count)
    print(f"FILE : {os.path.basename(args.pdf)}")
    print(f"PAGES: {doc.page_count} total, reading {len(pages)}")
    meta = doc.metadata or {}
    if meta.get("title"):
        print(f"TITLE: {meta['title']}")
    print()

    if args.png:
        os.makedirs(args.png, exist_ok=True)

    for i in pages:
        page = doc.load_page(i)
        text = (page.get_text() or "").strip()
        image_only = len(text) < TEXT_THRESHOLD
        print(f"===== PAGE {i + 1} ===== ({'image/drawing' if image_only else str(len(text)) + ' chars'})")
        if text:
            print(text[:args.max_chars])
            if len(text) > args.max_chars:
                print("...[TRUNCATED]")
        if args.png and (image_only or not args.only_images):
            pix = page.get_pixmap(dpi=args.dpi)
            out = os.path.join(args.png, f"p{i + 1:03d}.png")
            pix.save(out)
            print(f"[PNG] {out}  ({pix.width}x{pix.height})")
        print()

    doc.close()


if __name__ == "__main__":
    main()
