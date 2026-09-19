#!/usr/bin/env python3
"""
Pre-render every tikzpicture in the chapters to a PNG, so Pandoc can embed
them in the .docx.

Pandoc's LaTeX reader has no TikZ or pgfplots engine. It drops a
tikzpicture silently, which is why the Word output has been arriving with
the figures missing while the PDF has them. The fix is to compile each
picture standalone with the same preamble the thesis uses, rasterise it, and
substitute an \\includegraphics pointing at the result.

Writes:  figures/auto/tikz_<n>.png
Emits:   a JSON map from picture index to PNG path, consumed by
         tools/tex_for_docx.py.

Usage:   python3 tools/render_tikz.py            (renders all, caches by hash)
"""

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "figures" / "auto"
CACHE = OUT / ".cache.json"

# Same packages the pictures rely on in ubthesis.sty. standalone gives a
# tight bounding box, so the PNG carries no page margins.
PREAMBLE = r"""
\documentclass[border=2pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{newtxtext}
\usepackage{newtxmath}
\usepackage{tikz}
\usetikzlibrary{positioning, arrows.meta, shapes.geometric, fit, backgrounds, calc}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{siunitx}
% Pictures may use \gls and \cite. Load the real abbreviation definitions so
% \gls expands exactly as it does in the thesis. \cite has no bibliography to
% resolve against in a standalone compile, so it is suppressed; the citations
% for every figure are carried by its caption and surrounding text anyway.
\usepackage[abbreviations,nomain,nopostdot,nogroupskip]{glossaries-extra}
\setabbreviationstyle[abbreviation]{long-short}
\input{ABBREV}
\renewcommand{\cite}[2][]{\mbox{}}
\begin{document}
@@PICTURE@@
\end{document}
"""


def find_pictures(texts):
    """Return every tikzpicture body, in document order."""
    pat = re.compile(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", re.S)
    found = []
    for path, body in texts:
        for m in pat.finditer(body):
            found.append((path, m.group(0)))
    return found


def render(body, dest):
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        tex = (PREAMBLE.replace("ABBREV", str(HERE / "front" / "abbreviations"))
                       .replace("@@PICTURE@@", body))
        (td / "p.tex").write_text(tex, encoding="utf-8")
        r = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "p.tex"],
            cwd=td, capture_output=True, text=True,
        )
        pdf = td / "p.pdf"
        if not pdf.exists():
            log = (td / "p.log").read_text(errors="ignore") if (td / "p.log").exists() else r.stdout
            err = [l for l in log.splitlines() if l.startswith("!")][:3]
            return False, "; ".join(err) or "no PDF produced"
        subprocess.run(
            ["pdftoppm", "-png", "-r", "300", "-singlefile", str(pdf), str(dest.with_suffix(""))],
            check=True, capture_output=True,
        )
        return True, None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    texts = []
    for p in sorted((HERE / "chapters").glob("*.tex")) + sorted((HERE / "back").glob("*.tex")):
        texts.append((p, p.read_text(encoding="utf-8")))

    mapping, failures = {}, []
    for i, (src, body) in enumerate(find_pictures(texts), start=1):
        h = hashlib.sha256(body.encode()).hexdigest()[:16]
        dest = OUT / f"tikz_{i:02d}.png"
        if cache.get(str(dest)) == h and dest.exists():
            mapping[body] = str(dest.relative_to(HERE))
            print(f"  [cached] {dest.name}  ({src.name})")
            continue
        ok, err = render(body, dest)
        if ok:
            cache[str(dest)] = h
            mapping[body] = str(dest.relative_to(HERE))
            print(f"  [render] {dest.name}  ({src.name})")
        else:
            failures.append((src.name, err))
            print(f"  [FAIL]   {dest.name}  ({src.name}): {err}", file=sys.stderr)

    CACHE.write_text(json.dumps(cache, indent=1))
    (OUT / "map.json").write_text(json.dumps(
        [{"tex": k, "png": v} for k, v in mapping.items()], indent=1))
    print(f"rendered {len(mapping)} picture(s), {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
