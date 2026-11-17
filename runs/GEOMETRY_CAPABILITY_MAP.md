# GEOMETRY CAPABILITY MAP

Generated: 2026-11-16 (local repo, branch `main`, HEAD `af316d2`)
Method: file inspection + symbol inspection + executed tests + executed sandbox probe.
Status: EVIDENCE ONLY. This document authorizes no implementation.

## VERDICT

**A + B — partly exists under another name, partly exists as real code with tests.**

The Structural Discovery Core is NOT missing. `barrot_agent/geometry/` already
implements 5 of the 9 proposed layers as working, tested code:
representation, constraints, invariants, signature, relations/incidence.
It does NOT implement classification, stratification, representation
correspondence, or certificates. No `compare_invariants` exists anywhere in the
repo — the snapshot's "structural core" names (`EvidenceStage`,
`VerificationStatus`) do not exist. The equivalent semantics live under
different names: `EvidenceState` (8 states) and `TruthState` (4 states).

So: **the package is a real partial core, not a set of loose primitives, and not
the full proposed core.**

## MEASURED EVIDENCE

Production package — `barrot_agent/geometry/`, 677 lines:

```
0329d15edc82d33542e6aedcb66e83bcda5e0ee34cf905014e919f3c7ffa287a  __init__.py      54 lines
43f026ab99e87534ec3148b96bd6e8ef59446c475b0ff4d59274e6a3b336e16a  object.py        56 lines
75920ffe61d31be65dea60a9f909234b9345f07acbb07cf7da817ec3cd41f321  relations.py    182 lines
1f4b5a610f2b27b390dd288ee9465366dccabc5cd769a7a64eb64a6270e73f72  signature.py    210 lines
1011dd55c4066f7aaf67310dfa7b7a35eddfe294d95f48351e27ff04dd59a3de  states.py       175 lines
a3f29b822e6167de0039f97ac275595dd73a4829d22037374279454a601eff97  rendering/mesh_topology.py  (dependency)
```

Test execution (full modules, no `-k`):

```
pytest tests/test_geometry_{object,relations,signature,states}.py
72 passed, 0 failed           (4 / 11 / 17 / 19 tests per file)
pytest tests/test_mmi_contract.py tests/test_mmi_v1.py
32 passed, 0 failed
```

Coverage gate: `pytest.ini` requires 70% repo-wide; a 4-file subset measures
14.15%, so the run exits non-zero on the gate, not on a test. 72/72 tests pass.

Sandbox probe (`/tmp/opencode/geom_probe.py`, repo untouched) — 11/11:

```
PASS  relabel invariance x50
PASS  winding changes digest
PASS  translation changes digest (no false invariance claim)
PASS  provenance excluded from digest
PASS  same invariants != same digest
PASS  quad face rejected
PASS  None -> UNRESOLVED
PASS  contradiction stays UNRESOLVED + flag
PASS  UNRESOLVED outranks VALID
PASS  unwitnessed relation rejected
PASS  permutation bound refuses
```

## EXISTING_MATCHES

| Proposed capability | Actual evidence | File:line |
|---|---|---|
| A. Representation | `GeomObject` frozen dataclass, `kind` names the representation, validated on construction | `geometry/object.py:15` |
| C. Constraints | `evaluate_constraint(satisfied, violated, applicable)` — `None` is "no evidence", never false | `geometry/states.py:64` |
| D. Invariants | `INVARIANT_SETS["mesh.v1"]` = 6 named invariants; digest bound to set id | `geometry/signature.py:25` |
| E. Signature | `structural_signature()` → `Signature` with digest, set id, transform class, tolerance, provenance | `geometry/signature.py:173` |
| G. Relational structure | `RelationGraph` with 9 typed relations, witness required, symmetry/antisymmetry/irreflexivity/acyclicity declarations | `geometry/relations.py:14-182` |
| H. Incidence / boundary | `_incidence()` edge incidence; `BOUNDARY_OF`, `CLOSURE_OF` typed | `geometry/signature.py:77`, `relations.py:19-20` |
| Epistemic states | `EvidenceState` 8 states + `TruthState` 4 states + `combine()` precedence | `geometry/states.py:16-47` |
| Exact vs numerical | tolerance quantization + `MAX_PERMUTATIONS=1000` refuses rather than guessing | `geometry/signature.py:70-90` |
| Provenance independence | provenance returned but excluded from digest (proved by probe) | `geometry/signature.py:202-209` |
| Negative structure | `REFUTED` state, `is_watertight: False`, `degnerate_triangles`, `contradictory` flag | `states.py:104`, `signature.py:26-33` |

## PARTIAL_MATCHES

| Capability | What exists | What is absent |
|---|---|---|
| D. Invariant evaluation engine | invariants are *read* from `analyze_mesh_topology` output | no generic invariant evaluation over arbitrary structures; no `compare_invariants`; no equivalence API anywhere in repo (grep: 0 hits) |
| B. Domain / configuration space | `GeomObject.kind` names one domain; `INVARIANT_SETS` is a 1-entry registry | no declared domain/config-space model, no multiple domains, no parameter space |
| F. Classification | `RelationType.SPECIALIZES` + `is_watertight` boolean | no classifier, no class hierarchy, no `def classify` in the package (grep: 0) |
| I. Representation correspondence | exact-vs-numerical distinction exists | no cross-representation mapping; `correspondence` grep: 0 |

## LOW_LEVEL_PRIMITIVES_ONLY

- `barrot_agent/rendering/quality_metrics.py` — texture/material/performance
  validation for 3D assets. Geometry-adjacent QA, not structural discovery.
- `hover_bike_revolution/src/hover_bike_generator.py` — bounding-box generation.
- `barrot_agent/specialist_role_engine.py` — "sacred geometry" / "Euclidean
  geometry" strings are *domain knowledge labels*, not code semantics.
- `barrot_agent/ingestion/barrot_polymath_ingestion.py` — "knot theory
  invariants", "fractal mathematics" are *topic strings*.
- `apex_lattice/logs/*.log`, `brain_corpus/topics.txt`, `docs/ingestion.md` —
  prose/log mentions. A term in documentation is not a capability.
- `barrot_agent/ingestion/mmi_contract.py` — `EvidenceState` vocabulary is real
  and consumed by `geometry/states.py`, but it is a contract, not a discovery engine.

## REDUNDANCIES

- Two evidence vocabularies coexist: `mmi_contract.EvidenceState` (5 values) and
  `geometry.states.EvidenceState` (8 values), bridged explicitly by
  `from_mmi_evidence()`. Deliberate duplication with a mapping table — accepted,
  but a second table is a second thing to drift.
- `mmi_v1.ParseState` → `geometry.states.from_parse_state()`, same pattern.
- `TruthState.VALID/INVALID` overlaps `VerificationStatus` semantics from the
  snapshot. Only one implementation exists locally; no conflict.

## CONFLICTS

- **Snapshot vs disk.** The snapshot describes `.barrot/sources/mmi_original_ingest/*`,
  `.barrot/mmi_learning/*`, `scripts/barrot_governed_bundle_executor.py`,
  `tests/test_governed_bundle_executor.py`, branch `barrot/task`, two remotes, and
  three checkpoint commits. **None exist locally.** Verified:

  ```
  9a8b5f08... ABSENT   5fa5534e... ABSENT   3c0a9a66... ABSENT
  .barrot/sources/            MISSING   (.barrot has 83 files, no sources/, no mmi_learning/)
  barrot_governed_bundle_executor.py  MISSING (script and test)
  remotes: origin -> github only. NO gitlab remote.
  branch: main. No barrot/task.
  ```

  Conclusion: the snapshot is from a different clone (Termux-side or a remote
  branch not fetched). It is NOT authority over this tree. Nothing was reset.
- **Test-name conflict is unverifiable here.** `test_execution_requested_typed_bundle_executes`
  cannot be a contract mismatch because the module it lives in does not exist in
  this tree. Nothing to weaken; nothing to fix.

## DANGEROUS_ASSUMPTIONS

1. "Geometry package exists ⇒ Structural Discovery Core complete." False: 4 of 9
   layers absent.
2. "`structural_signature` proves equivalence." False and already guarded: digest
   is canonical-form-under-RELABEL only. Translation and winding change it (proved).
   No `equivalence_claim` field exists — absence of the field is the safeguard.
3. "Invariant match ⇒ same object." Probe disproved: two distinct shapes shared
   all 6 invariants and produced different digests.
4. "The rendering geometry code is the structural core." False: quality metrics
   and bounding boxes are QA/generation, not invariant reasoning.
5. "The snapshot's hashes are this repo's history." Unverifiable: all three
   commits absent.
6. "`UNKNOWN`/`None` can be treated as false." Guarded in code, but any new caller
   that passes `violated=False` where evidence is missing would manufacture a
   verdict. Callers must pass `None`.

## MISSING_CAPABILITIES

| Missing | Why it matters | Blocking? |
|---|---|---|
| B. Domain / configuration space | `INVARIANT_SETS` has exactly 1 entry; no way to declare a new domain | yes, for generality |
| F. Classification | relations exist, classes do not; `SPECIALIZES` is an edge with no classifier | yes, for stratification |
| Stratification / region discovery | grep: 0 hits in repo | yes |
| I. Representation correspondence | grep: 0 hits | yes |
| Certificates | grep: 0 hits; no artifact binding a claim to its proof | no |
| Perturbation / robustness | grep: 0 hits | deferred by design |
| Minimal sufficient explanation | absent | deferred by design |
| `compare_invariants` / equivalence | absent — and deliberately so | no; adding it needs an explicit "unverified" return |

## HIGH_VALUE_EXTENSIONS

1. **Second invariant set** (`INVARIANT_SETS["<domain>.v1"]`) — proves the
   registry is a registry and not a hardcoded single case. Small, testable.
2. **`Signature` comparison that returns `UNRESOLVED` unless invariant set id,
   transform class, tolerance AND digest match** — the safe form of
   `compare_invariants`, with `equivalence_claim = None` by construction.
3. **Domain-declared `GeomObject`** — `kind` already exists; add validation that
   the kind matches the invariant set used.
4. **Certificate record** — persist `(digest, invariant_set_id, tolerance,
   transform_class, provenance, test ids)` so a claim is reproducible.

## DEFERRED_CAPABILITIES

Grassmannians, positive Grassmannians, plabic graphs, triangulation,
amplituhedron, advanced correspondence, robustness, minimal explanation,
conjecture generation, cross-domain correspondence. Keep as extensions/tests.
No repository evidence justifies promoting any of them into the core.

## REQUIRED_TESTS

Before any new layer is merged:

1. Invariant-set registry: unknown id raises; adding a set does not change
   `mesh.v1` digests (regression on digest stability).
2. Relabel invariance for the new set, ×50 permutations.
3. Digest stability across process restarts (no `hash()`/`PYTHONHASHSEED` dependence).
4. Tolerance monotonicity: coarser tolerance never yields *more* distinctions.
5. `compare_invariants`-style API must return `UNRESOLVED` for same-invariants
   different-digest inputs (the probe case).
6. Classification: every class has a witness; no class without evidence.
7. Stratification: region membership is reproducible from the signature alone.
8. Correspondence: a mapping is rejected if the two signatures disagree on
   transform class or tolerance.

## MMI_INTEGRATION_CONTRACT

- Input: `mmi_contract.MMIEvidence` / `mmi_v1.ParseState` → `from_mmi_evidence()` /
  `from_parse_state()`. Never re-implement the mapping inline; the tables at
  `states.py:110-138` are the single bridge.
- Output: geometry claims carry `EvidenceState`, never a boolean truth.
  `VERIFIED` is reachable only through `verified_evidence(record)`.
- Contradictions travel as `ConstraintResult.contradictory=True` with state
  `UNRESOLVED`. Never resolve a contradiction silently.
- Provenance: `Signature.provenance` is carried but excluded from the digest, so
  provenance cannot be laundered into identity.
- Barrot-generated geometry output is not independent corroboration.
- Every capability map claim must cite file:line or an executed test.

## RECOMMENDED_MINIMUM_CORE

Present today (do not rebuild): A representation, C constraints, D invariants,
E signature, G relations, H incidence, epistemic states, exact-vs-numerical gate,
provenance separation.

Add only, in order, one at a time, each with tests:

1. Invariant-set registry with ≥2 real sets (makes B a capability).
2. Safe comparison API returning `UNRESOLVED` + `equivalence_claim=None`.
3. Classification with witnessed classes (enables F).
4. Stratification over classifications.
5. Certificate persistence.
6. Correspondence last — only after 1-5 are tested.

## WHAT THIS DOCUMENT DOES NOT AUTHORIZE

No implementation was performed. No production geometry file was modified.
The probe ran from `/tmp/opencode/` and imported the package read-only.
tau = 0.707 remains quarantined and unused.
