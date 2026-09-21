# BARROT V3 — SOURCE SET 01: FOUNDATIONS

This package is the **first source-acquisition set** for Barrot V3.

It is intentionally organized as a provenance-first acquisition manifest rather than pretending that web pages downloaded by this environment are authoritative local copies.

## Included sources

1. NIST AI RMF 1.0
2. NIST Generative AI Profile (AI 600-1)
3. OWASP GenAI LLM Top 10 2026
4. Model Context Protocol 2026-07-28
5. Agent2Agent Protocol 1.0.0
6. SLSA 1.2
7. in-toto specifications
8. OpenTelemetry
9. JSON Schema
10. pytest

## MMI handling

For each source, Barrot should preserve:

- publisher
- canonical URL
- exact version/date where available
- acquisition timestamp
- downloaded artifact SHA-256
- parser/version used
- parsable scope
- component hierarchy
- source/component depth through level 4
- extracted observations
- interpretations kept separate from observations
- corroborating sources
- contradictions
- unresolved gaps
- confidence/uncertainty
- resulting capability implications

## Source precedence

External material is **reference evidence**.

It must not silently replace:
- Barrot's mission
- Barrot's MMI protocol
- repository-verified implementation facts
- explicit governance boundaries
- validated execution evidence

## Recommended acquisition order

A. NIST AI RMF + NIST GAI Profile
B. OWASP GenAI LLM Top 10 2026
C. JSON Schema
D. SLSA + in-toto
E. MCP + A2A
F. OpenTelemetry
G. pytest

The first five groups directly support the architecture we are currently implementing.
