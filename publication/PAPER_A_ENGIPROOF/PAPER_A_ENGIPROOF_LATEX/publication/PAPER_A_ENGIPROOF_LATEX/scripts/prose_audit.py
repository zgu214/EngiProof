"""Style-only edit guard for the manuscript.

Compares the manuscript at a git revision (default: develop) with the working tree.
The following must be unchanged:
- numbers;
- citation keys;
- labels and cross-references;
- evidence identifiers (PA-xx, Fxx, Pxx, Pxx-Dxxx, Pxx-Cxxx, G1-G5, D-00x);
- evidence-class and status macros;
- inline mathematics;
- table bodies.

Usage (from this directory):  python scripts/prose_audit.py [REV]
Exit code 1 if any protected token changed.
"""
import collections, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
REPO = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=HERE, text=True).strip())
REL = HERE.relative_to(REPO).as_posix()
FILES = ["main.tex"] + [f"sections/{p.name}" for p in sorted((HERE / "sections").glob("*.tex")) if p.name != "a_claim_evidence.tex"]


def old_text(rev, rel):
    try:
        return subprocess.check_output(["git", "show", f"{rev}:{REL}/{rel}"], cwd=REPO, text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return ""


def strip_comments(t):
    return re.sub(r"(?<!\\)%.*", "", t)


def tokens(t):
    t = strip_comments(t)
    t = re.sub(r"\\begin\{(itemize|enumerate|description)\}\[[^\]]*\]", r"\\begin{\1}", t)  # layout options only
    tables = re.findall(r"\\begin\{tabular\}.*?\\end\{tabular\}", t, flags=re.S)
    tikz = re.findall(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", t, flags=re.S)
    body = re.sub(r"\\begin\{(tabular|tikzpicture)\}.*?\\end\{\1\}", " ", t, flags=re.S)
    math = re.findall(r"(?<!\\)\$[^$]+\$|\\\[.*?\\\]", body, flags=re.S)
    return {
        "numbers": collections.Counter(re.findall(r"(?<![A-Za-z\\\d.,])\d+(?:[.,]\d+)*", re.sub(r"\\(?:ref|label|cite)\{[^}]*\}", "", body))),
        "cite keys": collections.Counter(k.strip() for c in re.findall(r"\\cite\{([^}]*)\}", body) for k in c.split(",")),
        "labels": collections.Counter(re.findall(r"\\label\{([^}]*)\}", t)),
        "refs": collections.Counter(re.findall(r"\\ref\{([^}]*)\}", body)),
        "evidence ids": collections.Counter(re.findall(r"\b(?:PA-\d\d|P\d\d(?:-[DC]\d{3})?|F\d{1,2}|G[1-5]|D-00\d)\b", body)),
        "class/status macros": collections.Counter(re.findall(r"\\e(?:class|status)\{[^}]*\}", body)),
        "inline math": collections.Counter(m.strip() for m in math),
        "table bodies": collections.Counter(re.sub(r"\s+", " ", x) for x in tables),
        "figures (tikz)": collections.Counter(re.sub(r"\s+", " ", x) for x in tikz),
    }


def main():
    rev = sys.argv[1] if len(sys.argv) > 1 else "develop"
    old = tokens("\n".join(old_text(rev, f) for f in FILES))
    new = tokens("\n".join((HERE / f).read_text(encoding="utf-8") for f in FILES))
    bad = False
    for k in old:
        if old[k] != new[k]:
            bad = True
            lost, added = old[k] - new[k], new[k] - old[k]
            print(f"CHANGED {k}:\n  removed {dict(lost)}\n  added   {dict(added)}")
        else:
            print(f"ok      {k} ({sum(old[k].values())})")
    def words(fs, reader):
        return sum(len(strip_comments(reader(f)).split()) for f in fs)
    print(f"words: {words(FILES, lambda f: old_text(rev, f))} -> {words(FILES, lambda f: (HERE / f).read_text(encoding='utf-8'))}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
