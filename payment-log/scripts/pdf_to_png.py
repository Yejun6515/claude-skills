# Render each page of a PDF to PNG so the Read tool can look at it.
# Needed because PO / contract PDFs from PTKR are scanned images — text extraction returns nothing.
# Usage: <venv>\python.exe pdf_to_png.py <input.pdf> <output_prefix> [resolution]
import sys
import pdfplumber

src = sys.argv[1]
prefix = sys.argv[2]
res = int(sys.argv[3]) if len(sys.argv) > 3 else 180

with pdfplumber.open(src) as pdf:
    for i, page in enumerate(pdf.pages, 1):
        text = (page.extract_text() or "").strip()
        out = f"{prefix}_p{i}.png"
        page.to_image(resolution=res).save(out)
        print(f"{out}\tTEXT_CHARS={len(text)}")
