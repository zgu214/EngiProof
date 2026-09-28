"""Check that the numbers the manuscript prose states agree with repository data (WORK_QUEUE Q11 step 3).

Run from this directory:  python scripts/check_manuscript_facts.py

Each check builds the exact phrase the prose must contain from generated/facts.json
(written by scripts/build_tables.py from the repository). If the repository changes,
the phrase changes and the check fails until the prose is corrected and traced in
MANUSCRIPT_STATUS.md. The script never edits the manuscript or any evidence file.

Findings that need an owner decision are listed in OPEN_FINDINGS: they are reported
as OPEN (not PASS) and do not fail the run; if one starts passing, the run fails so
that the entry is removed and the resolution traced.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
         10: "ten", 11: "eleven", 12: "twelve"}

OPEN_FINDINGS = {}  # SA-2 resolved 28 September 2026 (owner decision, option a); see MANUSCRIPT_STATUS.md


def text(rel):
    return (HERE / rel).read_text(encoding="utf-8")


def main():
    if subprocess.run([sys.executable, str(HERE / "scripts/build_tables.py"), "--check"]).returncode:
        print("FAIL generated tables/facts are stale: run scripts/build_tables.py")
        return 1
    f = json.loads(text("generated/facts.json"))
    c, d = f["comparisons"], f["decisions_by_disposition"]
    ds = f["discrepancies_paper_a_by_status"]
    r = f["readiness"]
    W = lambda n: WORDS.get(n, str(n))

    checks = [  # (id, file, phrase that must occur)
        ("abstract-reproduced-compared", "sections/00_abstract.tex",
         f"reproduce {c['REPRODUCED']} targets to source precision and compare {c['COMPARED']} more"),
        ("abstract-discrepancies", "sections/00_abstract.tex", f"{f['discrepancies_paper_a']} discrepancy records"),
        ("s4-comparison-total", "sections/04_reproduction.tex", f"there are {f['comparisons_total']} comparison records"),
        ("s4-comparison-split", "sections/04_reproduction.tex",
         f"of which {c['REPRODUCED']} are \\estatus{{REPRODUCED}}, {c['COMPARED']} \\estatus{{COMPARED}}, "
         f"{c['CONDITIONAL']} \\estatus{{CONDITIONAL}}"),
        ("s3-readiness", "sections/03_ingestion.tex",
         f"P40 ({r['P40'][0]} of {r['P40'][1]}), P41 ({r['P41'][0]} of {r['P41'][1]}) and P42 ({r['P42'][0]} of {r['P42'][1]})"),
        ("s3-readiness-partial", "sections/03_ingestion.tex",
         f"P43 ({r['P43'][0]} of {r['P43'][1]}), P44 ({r['P44'][0]} of {r['P44'][1]}) and P45 ({r['P45'][0]} of {r['P45'][1]})"),
        ("s3-p45-readiness", "sections/03_ingestion.tex", f"reached only {r['P45'][0]} of {r['P45'][1]} selected targets"),
        ("s6-discrepancy-counts", "sections/06_discrepancies.tex",
         f"The six studies hold {f['discrepancies_paper_a']} records, {ds.get('OPEN', 0)} \\estatus{{OPEN}} and "
         f"{W(ds.get('OBSERVED', 0))} \\estatus{{OBSERVED}}, and the repository as a whole holds {f['discrepancies_repository']}."),
        ("s6-taxonomy-categories", "sections/06_discrepancies.tex", f"There are {W(f['taxonomy_categories'])}, each with a definition"),
        ("s6-taxonomy-loci", "sections/06_discrepancies.tex", f"there are {W(f['taxonomy_loci'])}, and a record may have several"),
        ("s6-taxonomy-approved", "sections/06_discrepancies.tex", f"mapping of all {f['taxonomy_approved']} records"),
        ("s6-decisions-total", "sections/06_discrepancies.tex", f"{W(f['decisions_total']).capitalize()} real decisions have been recorded"),
        ("s6-decisions-accepted", "sections/06_discrepancies.tex", f"{W(d.get('ACCEPTED_WITH_RATIONALE', 0)).capitalize()} were accepted with rationale"),
        ("s6-decisions-deferred", "sections/06_discrepancies.tex", f"The remaining {W(d.get('DEFERRED', 0))} decisions keep the block"),
        ("s7-graph-nodes", "sections/07_provenance.tex", f"{f['graph_nodes_min']}--{f['graph_nodes_max']} nodes"),
        ("s8-crossenv", "sections/08_nonmutating.tex",
         f"all {f['crossenv_studies'][0]} studies in the repository verify in {W(f['crossenv_environments'])} environments with no material artifact"),
        ("s10-failure-modes", "sections/10_failures_limits.tex", f"recorded {f['failure_modes']} failure modes"),
        ("s2-evidence-status", "sections/02_framework.tex", "the evidence status is \\estatus{CONDITIONAL} for all six cases"),
        ("qualification-all-six", "sections/11_qualification.tex",
         "Every study manifest and evidence graph records engineering qualification as \\estatus{NOT\\_GRANTED}, "
         "as does every result artifact that carries a qualification field"),
        ("s2-qualification-field", "sections/02_framework.tex",
         "a separate qualification field is \\estatus{NOT\\_GRANTED} for all six"),
    ]
    # conditions a phrase alone cannot express
    conditions = {
        "s6-decisions-total": sum(d.values()) == f["decisions_total"],
        "s8-crossenv": len(f["crossenv_studies"]) == 1 and f["crossenv_material"] == 0,
        "s10-failure-modes": f["failure_ids_contiguous"],
        "s2-evidence-status": f["evidence_status"] == ["CONDITIONAL"],
        "s7-graph-nodes": f["graph_coverage_all"] == [1.0],
        "qualification-all-six": set(f["qualification_by_study"].values()) == {"NOT_GRANTED"}
                                 and set(f["graph_qualification_by_study"].values()) == {"NOT_GRANTED"}
                                 and f["result_qualification_values"] == ["NOT_GRANTED"],
        "s2-qualification-field": not f["manifests_without_qualification_field"]
                                  and set(f["qualification_by_study"].values()) == {"NOT_GRANTED"},
    }
    failed = 0
    for cid, rel, phrase in checks:
        ok = phrase in text(rel) and conditions.get(cid, True)
        if cid in OPEN_FINDINGS:
            if ok:
                print(f"FAIL {cid}: listed as an open finding but now passes; remove it from OPEN_FINDINGS and trace the resolution")
                failed += 1
            else:
                print(f"OPEN {cid}: {OPEN_FINDINGS[cid]}")
            continue
        print(("PASS " if ok else "FAIL ") + f"{cid} [{rel}]" + ("" if ok else f": expected phrase not found or condition false: {phrase!r}"))
        failed += not ok
    print(f"{len(checks) - failed - len(OPEN_FINDINGS)} passed, {failed} failed, {len(OPEN_FINDINGS)} open")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
