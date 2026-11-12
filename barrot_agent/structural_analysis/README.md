# Structural Analysis Core

This package provides deterministic, evidence-aware structural descriptors for Barrot V3. It is a reusable analysis kernel, not a general theorem prover and not an implementation of Grassmannians, cell decompositions, or a universal equivalence decision procedure.

The processing boundary is:

`representation → constraints → invariants → structural relations → deterministic signature → verification boundary`

## Guarantees

- Typed evidence stages, verification statuses, constraints, invariants, and relations.
- Non-negative integer dimension/codimension metadata.
- Strict JSON-safe canonicalization for supported primitive, mapping, sequence, enum, and dataclass values.
- Deterministic descriptor signatures that include provenance and all descriptor metadata.
- Bounded configured evaluator count and result-type checks.
- Duplicate invariant names are retained during comparison.
- Descriptor matches never become an equivalence claim automatically.

## Limits

- A descriptor signature identifies the recorded descriptor/provenance set, not necessarily the raw mathematical object.
- Similar or matching invariants do not prove equality, isomorphism, homeomorphism, or any other relation.
- A relation is only verified when an independent method, criterion, and appropriate witness are supplied and its verification status is explicitly established.
- Domain-specific mathematical evaluators must be independently validated and must report uncertainty honestly.
- The evaluator budget limits configured evaluator count; it is not a runtime sandbox for evaluator execution.

No external mathematics, physical constant, or system-wide invariant is assumed by this package.
