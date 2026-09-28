"""Build the Paper A submission package for Advances in Engineering Software.

Run from the manuscript directory:  python scripts/build_submission_package.py

Writes to publication/PAPER_A_ENGIPROOF/SUBMISSION_PACKAGE/out/ (not tracked):
  EngiProof_PaperA_manuscript.pdf        clean build of main.tex
  EngiProof_PaperA_latex_source.zip      self-contained LaTeX source, test-compiled from the zip contents
  EngiProof_PaperA_highlights.docx       highlights as a separate editable file (read from main.tex)
  EngiProof_PaperA_declaration_of_interest.docx
  EngiProof_PaperA_cover_letter.docx / .pdf   from ../../../SUBMISSION_PACKAGE/cover_letter.md
  MANIFEST.txt                           git commit, package checks and SHA-256 of every file

The script checks the facts, the generated tables, the highlights (3-5 items, each <= 85 characters),
the keywords (<= 6) and that the build has no undefined references. It never edits the manuscript or
any evidence file.
"""
import datetime, hashlib, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

from docx import Document
from docx.shared import Cm, Pt

HERE = Path(__file__).resolve().parent.parent
PKG = HERE.parents[2] / "SUBMISSION_PACKAGE"
OUT = PKG / "out"
PREFIX = "EngiProof_PaperA_"
TITLE = ("EngiProof: A provenance-preserving framework for converting published engineering research "
         "into reproducible computational evidence")
AUTHOR = "Zhiqiang Gu"
DECLARATION = ("The author declares that he has no known competing financial interests or personal "
               "relationships that could have appeared to influence the work reported in this paper.")


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"FAILED: {' '.join(cmd)}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    return r.stdout


def latex_build(d):
    for f in d.glob("main.*"):
        if f.suffix not in (".tex",):
            f.unlink()
    run(["pdflatex", "-interaction=nonstopmode", "main.tex"], d)
    run(["bibtex", "main"], d)
    for _ in range(2):
        run(["pdflatex", "-interaction=nonstopmode", "main.tex"], d)
    log = (d / "main.log").read_text(encoding="latin-1")
    undefined = len(re.findall(r"undefined", log))
    if undefined:
        sys.exit(f"FAILED: {undefined} 'undefined' messages in {d / 'main.log'}")
    pages = int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", "main.pdf"], d)).group(1))
    return pages


def front_matter():
    tex = (HERE / "main.tex").read_text(encoding="utf-8")
    hl = re.search(r"\\begin\{highlights\}(.*?)\\end\{highlights\}", tex, re.S).group(1)
    highlights = [h.strip() for h in hl.split(r"\item")[1:]]
    kw = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", tex, re.S).group(1)
    keywords = [k.strip() for k in kw.split(r"\sep") if k.strip()]
    assert 3 <= len(highlights) <= 5 and all(len(h) <= 85 for h in highlights), highlights
    assert len(keywords) <= 6, keywords
    assert all("\\" not in h for h in highlights), "highlights must be plain text"
    return highlights, keywords


def base_doc():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    return doc


def heading(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(14)


def highlights_docx(highlights, path):
    doc = base_doc()
    heading(doc, "Highlights")
    doc.add_paragraph(TITLE).runs[0].italic = True
    for h in highlights:
        doc.add_paragraph(h, style="List Bullet")
    doc.save(path)


def declaration_docx(path, date):
    doc = base_doc()
    heading(doc, "Declaration of interests")
    doc.add_paragraph(f"Manuscript: {TITLE}")
    doc.add_paragraph(f"Author: {AUTHOR}")
    doc.add_paragraph("\u2612 " + DECLARATION)
    doc.add_paragraph(f"{AUTHOR}, {date}")
    doc.save(path)


def cover_letter_docx(path, date):
    src = (PKG / "cover_letter.md").read_text(encoding="utf-8")
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S).strip().replace("{date}", date)
    doc = base_doc()
    doc.styles["Normal"].font.size = Pt(11)
    doc.styles["Normal"].paragraph_format.space_after = Pt(6)
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.5)
        s.top_margin = s.bottom_margin = Cm(2.0)
    for block in re.split(r"\n\s*\n", src):
        p = doc.add_paragraph()
        for i, line in enumerate(block.strip().split("\n")):
            if i:
                p.add_run().add_break()
            p.add_run(line.strip())
    doc.save(path)


def source_zip(path):
    """Zip the manuscript sources and prove the zip compiles on its own."""
    files = [HERE / "main.tex", HERE / "references.bib", HERE / "main.bbl"]
    files += sorted((HERE / "sections").glob("*.tex")) + sorted((HERE / "generated").glob("*.tex"))
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f.relative_to(HERE).as_posix())
    with tempfile.TemporaryDirectory() as t:
        with zipfile.ZipFile(path) as z:
            z.extractall(t)
        pages = latex_build(Path(t))
    return len(files), pages


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    date = datetime.date.today().strftime("%d %B %Y").lstrip("0")
    run([sys.executable, "scripts/build_tables.py", "--check"], HERE)
    facts = run([sys.executable, "scripts/check_manuscript_facts.py"], HERE).strip().splitlines()[-1]
    highlights, keywords = front_matter()
    pages = latex_build(HERE)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copy(HERE / "main.pdf", OUT / f"{PREFIX}manuscript.pdf")
    nfiles, zip_pages = source_zip(OUT / f"{PREFIX}latex_source.zip")
    assert zip_pages == pages, (zip_pages, pages)
    highlights_docx(highlights, OUT / f"{PREFIX}highlights.docx")
    declaration_docx(OUT / f"{PREFIX}declaration_of_interest.docx", date)
    cl = OUT / f"{PREFIX}cover_letter.docx"
    cover_letter_docx(cl, date)
    run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(OUT), str(cl)], OUT)
    cl_pages = int(re.search(r"Pages:\s+(\d+)", run(["pdfinfo", str(cl.with_suffix(".pdf"))], OUT)).group(1))
    assert cl_pages == 1, f"cover letter is {cl_pages} pages"
    commit = run(["git", "rev-parse", "HEAD"], HERE).strip()
    dirty = run(["git", "status", "--porcelain", "--", "."], HERE).strip()
    lines = [f"Paper A submission package, built {date}",
             f"git commit: {commit}" + (" (manuscript directory has uncommitted changes)" if dirty else ""),
             f"manuscript: {pages} pages, 0 undefined references; source zip: {nfiles} files, compiles to {zip_pages} pages",
             f"highlights: {len(highlights)} ({', '.join(str(len(h)) for h in highlights)} characters); keywords: {len(keywords)}",
             f"facts check: {facts}", ""]
    lines += [f"{sha256(f)}  {f.name}" for f in sorted(OUT.iterdir()) if f.name != "MANIFEST.txt"]
    (OUT / "MANIFEST.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
