#!/usr/bin/env python3
"""Millennium database audit and consolidation.

Reads every acquired Millennium file and emits one ledger. It does not solve
anything and it does not grade mathematics; it records what the database actually
contains, flags disagreements, and attaches the blocking gap that any serious
attempt has to get past.

Sources read:
  data/millennium_problem_*.json   one file per problem
  data/millennium_problems_overview.json
  data/millennium_problems_unified.json
  data/millennium_problems_taxonomy.json
  data/research/millennium_claims_seed.jsonl
  data/research/{riemann,navier_stokes,anthropic_fermat}*.json
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "millennium" / "ledger.json"

CANONICAL = [
    (7, "Poincare Conjecture", "resolved"),
    (1, "P vs NP", "open"),
    (2, "Hodge Conjecture", "open"),
    (3, "Riemann Hypothesis", "open"),
    (4, "Yang-Mills Existence and Mass Gap", "open"),
    (5, "Navier-Stokes Existence and Smoothness", "open"),
    (6, "Birch and Swinnerton-Dyer Conjecture", "open"),
]

BLOCKING_GAP = {
    "P vs NP": "Three barrier theorems (relativization, natural proofs, algebrization) rule out every known technique; current circuit lower bounds do not reach NP.",
    "Hodge Conjecture": "The integral form is false (Atiyah-Hirzebruch torsion, Kollar); the rational form has no general construction of algebraic cycles in codimension two and higher.",
    "Riemann Hypothesis": "No archimedean positivity and no exact trace formula for the integers; the function field analogue is settled, the number field case is not.",
    "Yang-Mills Existence and Mass Gap": "No nonperturbative construction of a four-dimensional gauge theory, and no control of the renormalization group flow sufficient to prove a gap.",
    "Navier-Stokes Existence and Smoothness": "The equation is supercritical: the energy is invariant at the critical scaling and no monotone quantity rules out blow-up in three dimensions.",
    "Birch and Swinnerton-Dyer Conjecture": "Rank zero and one are known through Gross-Zagier and Kolyvagin; rank two and above need Euler systems or p-adic constructions that do not exist in general.",
}

TRANSMUTED_APPROACH = {
    "P vs NP": "Borrow the Poincare pattern - a deformation with a monotone quantity and controlled singularities - as an analogy only, then pursue geometric complexity theory (representation-theoretic obstructions), which is deliberately non-relativizing and non-naturalizing. Dead end to check first: occurrence obstructions already block the simplest GCT programme.",
    "Hodge Conjecture": "Use Poincare-style reduction to a normal form: replace cycle construction with a deformation of the Hodge structure (variation of Hodge structure) and ask which classes are invariant under monodromy. Test on the known counterexamples before general claims.",
    "Riemann Hypothesis": "De Bruijn-Newman flow: zeros evolve under a heat-type equation; RH is equivalent to Lambda = 0, and Lambda >= 0 is a theorem (Rodgers-Tao). The missing piece is a monotone quantity at t = 0, which is the same shape of gap that Ricci flow had.",
    "Yang-Mills Existence and Mass Gap": "Constructor path: Osterwalder-Schrader reconstruction plus a rigorous Wilsonian renormalization group flow; the monotone quantity is the effective action under scale. Test the flow on the lattice first, where the gap is already seen numerically.",
    "Navier-Stokes Existence and Smoothness": "Critical-space scaling: work in the scaling-invariant norm and look for a monotone (or at least non-increasing) functional along the flow, as with Ricci flow entropy. Dead end to record: mere energy methods cannot work, they are supercritical.",
    "Birch and Swinnerton-Dyer Conjecture": "Euler systems are the working analogue of a monotone quantity: each level yields a divisibility that improves with rank. Dead end: rank two Euler systems are not available; p-adic Iwasawa theory covers only parts of the picture.",
}

KPI_GATE = {
    "resolved": "A resolved problem is recorded only with a published proof and an independent verification event; here Poincare has both.",
    "open": "No progress claim is recorded without one of: a machine-checked lemma, a verified computation with a reproducible script, or a fetched peer-reviewed citation quoted in full.",
}


def resolved_like(text: str) -> bool:
    """The database says SOLVED, the ledger says resolved. Treat both as one."""
    low = normalize(text)
    return "solv" in low or "resolv" in low


def normalize(text: str) -> str:
    """Accent-insensitive lowercase, so Poincare matches Poincaré."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower().strip()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_seed(path: Path) -> tuple[list[dict], str | None]:
    records: list[dict] = []
    if not path.exists():
        return records, "missing"
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            return records, f"line {number}: {exc.msg}"
    return records, None


def count_records(node) -> int:
    if isinstance(node, list):
        return len(node)
    if isinstance(node, dict):
        return sum(count_records(v) for v in node.values() if isinstance(v, (list, dict)))
    return 0


def main() -> int:
    per_problem = {}
    for path in sorted(DATA.glob("millennium_problem_*.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError as exc:
            per_problem[path.name] = {"error": exc.msg}
            continue
        per_problem[path.name] = {
            "name": payload.get("name"),
            "status": payload.get("official_status"),
            "stage": payload.get("barrot_analysis_stage") or payload.get("progress_status"),
            "keys": sorted(payload),
        }

    overview_path = DATA / "millennium_problems_overview.json"
    overview = load_json(overview_path) if overview_path.exists() else []
    overview_status = {row.get("name", ""): row.get("status") for row in overview if isinstance(row, dict)}

    seed_records, seed_error = load_seed(DATA / "research" / "millennium_claims_seed.jsonl")

    bundles = {}
    for path in sorted((DATA / "research").glob("*.json")):
        try:
            payload = load_json(path)
        except json.JSONDecodeError as exc:
            bundles[path.name] = {"error": exc.msg}
            continue
        bundles[path.name] = {"records": count_records(payload), "top_keys": sorted(payload)}

    conflicts = []
    for number, name, status in CANONICAL:
        short = normalize(name).replace("-", " ").split()[0]
        for filename, row in per_problem.items():
            if "error" in row:
                continue
            if row.get("name") and short in normalize(str(row["name"])):
                if status == "resolved" and not resolved_like(str(row.get("status", ""))):
                    conflicts.append(f"{name}: file status says {row.get('status')!r}")
        for filename, value in overview_status.items():
            if value and short in normalize(filename) and status == "resolved" and not resolved_like(str(value)):
                conflicts.append(f"{name}: overview status says {value!r}")

    problems = [
        {
            "number": number,
            "name": name,
            "status": status,
            "blocking_gap": BLOCKING_GAP.get(name, "Resolved."),
            "transmuted_approach": TRANSMUTED_APPROACH.get(name, "Reference only; no new approach proposed."),
            "kpi_gate": KPI_GATE[status],
        }
        for number, name, status in CANONICAL
    ]

    claims_dir = DATA / "millennium" / "claims"
    for problem in problems:
        slug = normalize(problem["name"]).replace(" ", "_").replace("-", "_")
        path = claims_dir / f"{slug}.json"
        if not path.exists():
            continue
        payload = load_json(path)
        grades: dict[str, int] = {}
        for record in payload.get("records", []):
            grades[record.get("status", "?")] = grades.get(record.get("status", "?"), 0) + 1
        problem["evidence"] = {
            "file": str(path.relative_to(ROOT)),
            "method": payload.get("method"),
            "grades": grades,
            "usable_claims": grades.get("Q", 0),
            "rule": "only Q (quoted primary) records may support a claim",
        }

    ledger = {
        "generated_at": "2026-11-17",
        "database": {
            "problem_files": len(per_problem),
            "overview_rows": len(overview),
            "seed_records": len(seed_records),
            "seed_error": seed_error,
            "bundles": bundles,
        },
        "problems": problems,
        "conflicts": conflicts,
        "database_thinness": "Per-problem files contain narrative keys only (why_matters, next_steps). No proof, lemma, citation or machine-checked artifact exists in the acquired files. data/millennium/claims is new work under reverse-engineering v2 and is graded separately; only Q records there may support a claim.",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(json.dumps({k: ledger[k] for k in ("database", "conflicts")}, indent=2))
    print("ledger:", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
