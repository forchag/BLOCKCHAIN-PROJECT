#!/usr/bin/env python3
"""
Expand glossaries-extra commands into plain text before handing a .tex file
to Pandoc.

Pandoc does not understand \\gls, \\glspl, \\Gls or \\glsxtrshort/\\glsxtrlong,
and silently drops them, which would strip every abbreviation out of the .docx.
This script rewrites them using the definitions in front/abbreviations.tex,
reproducing glossaries' first-use behaviour:

    first occurrence   \\gls{crt}  ->  Chinese Remainder Theorem (CRT)
    later occurrences  \\gls{crt}  ->  CRT

Usage:  python3 tools/expand_gls.py input.tex output.tex
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ABBREV = HERE / "front" / "abbreviations.tex"

DEF_RE = re.compile(r"\\newabbreviation\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}")
USE_RE = re.compile(r"\\(gls|glspl|Gls|Glspl|glsxtrshort|glsxtrlong)\{([^}]+)\}")


def load_definitions():
    if not ABBREV.exists():
        sys.exit(f"not found: {ABBREV}")
    defs = {}
    for key, short, long in DEF_RE.findall(ABBREV.read_text(encoding="utf-8")):
        defs[key] = (short, long)
    return defs


def substitute_tikz(text):
    """Replace each tikzpicture with an \\includegraphics of its rendered PNG.

    Pandoc has no TikZ or pgfplots engine and drops the environment silently,
    which is why the Word output arrived with figures missing while the PDF had
    them. tools/render_tikz.py compiles each picture standalone and rasterises
    it; this swaps the picture for that image.

    Matching is on whitespace-normalised bodies, not exact strings: latexpand
    reflows the source when it flattens, so an exact comparison against
    map.json silently misses most pictures.
    """
    import json
    mp = HERE / "figures" / "auto" / "map.json"
    if not mp.exists():
        print("    warning: figures/auto/map.json missing; run tools/render_tikz.py",
              file=sys.stderr)
        return text

    def norm(t):
        # latexpand strips LaTeX comments when it flattens, so they have to go
        # here too or every picture carrying one fails to match.
        t = re.sub(r"(?<!\\\\)%.*?$", "", t, flags=re.M)
        return re.sub(r"\s+", " ", t).strip()

    table = {norm(i["tex"]): i["png"] for i in json.loads(mp.read_text())}
    pat = re.compile(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", re.S)

    hits = [0, 0]

    def repl(m):
        png = table.get(norm(m.group(0)))
        if png is None:
            hits[1] += 1
            return m.group(0)
        hits[0] += 1
        return "\\includegraphics[width=\\linewidth]{%s}" % png

    text = pat.sub(repl, text)
    msg = f"    substituted {hits[0]} TikZ picture(s) with rendered PNGs"
    if hits[1]:
        msg += f"; {hits[1]} unmatched (re-run tools/render_tikz.py)"
    print(msg)
    return text


def strip_titlesec(text):
    """Delete \\titleformat and \\titlespacing blocks.

    Pandoc's LaTeX reader cannot parse titlesec's argument syntax and aborts on
    it. The commands only affect typeset appearance, which reference.docx
    supplies for the Word output.

    Brace counting alone does not work: the first line of a \\titleformat is
    itself balanced ("{\\chapter}[display]"), so the argument lines that follow
    would be left orphaned. Drop the command line, then keep dropping the
    continuation lines, which always begin with "{" or "[".
    """
    kept, dropping = [], False
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith(("\\titleformat", "\\titlespacing")):
            dropping = True
            continue
        if dropping:
            if stripped.startswith(("{", "[")):
                continue
            dropping = False
        kept.append(line)
    return "".join(kept)


def expand(text, defs):
    seen = set()
    unknown = set()

    def repl(m):
        cmd, key = m.group(1), m.group(2)
        if key not in defs:
            unknown.add(key)
            return key.upper()
        short, long = defs[key]

        if cmd == "glsxtrshort":
            return short
        if cmd == "glsxtrlong":
            return long

        plural = cmd.endswith("pl")
        capital = cmd[0] == "G"

        if key in seen:
            out = short + ("s" if plural else "")
        else:
            seen.add(key)
            head = long + ("s" if plural else "")
            if capital:
                head = head[0].upper() + head[1:]
            out = f"{head} ({short}{'s' if plural else ''})"
        return out

    return USE_RE.sub(repl, text), unknown


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    defs = load_definitions()
    raw = src.read_text(encoding="utf-8")
    raw = substitute_tikz(raw)          # before expand(): map.json keys still
                                        # contain \gls, which expand() rewrites
    out, unknown = expand(raw, defs)

    # Replace \printunsrtglossary with an explicit description list, so the
    # List of Abbreviations survives into the .docx instead of vanishing.
    table = "\\begin{description}\n" + "".join(
        f"  \\item[{short}] {long}\n" for short, long in defs.values()
    ) + "\\end{description}"
    # lambda, not a literal replacement: backslashes in `table` would
    # otherwise be read as regex escapes.
    out = re.sub(r"^\\printunsrtglossary.*$", lambda _: table, out, flags=re.M)
    out = re.sub(r"^\\glsresetall.*$", "", out, flags=re.M)

    # Pandoc's LaTeX reader cannot parse titlesec's \titleformat argument
    # syntax and aborts on it. These commands only affect typeset appearance,
    # which the reference.docx supplies for the Word output, so strip them.
    out = strip_titlesec(out)

    # \ubsoft is defined in ubthesis.sty, so Pandoc drops it and the lettered
    # sub-headings disappear from the Word file. Map it onto an unnumbered
    # subsection, generating the a), b), c) letters here because LaTeX's
    # counter is not available; the counter resets at every \section, exactly
    # as \newcounter{ubsoft}[section] does.
    def _ubsoft(text):
        out, letter = [], 0
        for line in text.splitlines(keepends=True):
            if line.lstrip().startswith("\\section"):
                letter = 0
            m = re.match(r"\s*\\ubsoft\{(.*)\}\s*$", line)
            if m:
                out.append("\\subsection*{%s) %s}\n"
                           % (chr(ord("a") + letter), m.group(1)))
                letter += 1
                continue
            out.append(line)
        return "".join(out)

    out = _ubsoft(out)

    # \ubfrontheading is defined in ubthesis.sty, which Pandoc does not read,
    # so front-matter headings (CERTIFICATION, ABSTRACT, ...) would disappear.
    # Map it onto an unnumbered section Pandoc understands.
    out = re.sub(r"\\ubfrontheading\{([^}]*)\}",
                 lambda m: r"\section*{" + m.group(1).upper() + "}", out)

    dst.write_text(out, encoding="utf-8")
    if unknown:
        print(f"    warning: undefined abbreviation keys: {', '.join(sorted(unknown))}",
              file=sys.stderr)
    print(f"    expanded {len(defs)} abbreviation definitions -> {dst.name}")


if __name__ == "__main__":
    main()
