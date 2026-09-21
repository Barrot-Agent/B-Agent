# Barrot V3 Structural Analysis Core v1.1

Refinement of the first kernel. This remains intentionally small: it provides reusable evidence-aware structural descriptors, not a general theorem prover or an implementation of Grassmannians/cell decompositions.

Adds:
- explicit typed relations and verification status;
- dimension/codimension fields with basic validation;
- order-independent deterministic signatures;
- invariant comparison that never upgrades descriptor agreement into equivalence;
- bounded evaluator configuration checked at construction time;
- provenance preserved in signatures.

Architecture: representation → constraints → invariants → structural relations → signature → verification boundary.

No production B-Agent files are overwritten by this bundle. Integrate only after mapping against the actual checkout and running the repository's relevant tests.
