# Barrot V3 Structural Analysis Core v1.1

Integrated as a small deterministic kernel for evidence-aware structural analysis. It provides typed constraints, invariants, relations, dimensions/codimensions, deterministic signatures, and provenance binding.

**Verification boundary:** matching descriptors are not a proof of equivalence. LLM output is not proof. The kernel does not implement a general theorem prover, Grassmannians, or cell decompositions. Domain-specific evaluators must be supplied and independently validated.

Architecture: representation → constraints → invariants → structural relations → signature → verification boundary.

## Foundation source set 01 (provenance-first acquisition manifest)

The source set is a manifest of external references, not a claim that all pages/PDFs were downloaded or fully ingested. External references never override Barrot's mission, MMI contract, governance, or repository-verified facts.

| Source ID | Publisher / version | Official reference | Intended use |
|---|---|---|---|
| NIST-AI-100-1 | NIST AI RMF 1.0 | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10 | Risk governance, measurement, lifecycle controls |
| NIST-AI-600-1 | NIST AI 600-1 | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence | Generative-AI risk and trustworthiness |
| OWASP-GENAI-LLM-2026 | OWASP GenAI LLM Top 10 (2026) | https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ | Agent and LLM application security |
| MCP-2026-07-28 | MCP Specification, 2026-07-28 | https://modelcontextprotocol.io/specification/2026-07-28 | Tool/resource/prompt interoperability |
| A2A-1.0.0 | Agent2Agent 1.0.0 | https://a2a-protocol.org/latest/specification/ | Agent discovery and task exchange |
| SLSA-1.2 | SLSA 1.2 | https://slsa.dev/spec/v1.2/ | Supply-chain provenance and attestations |
| IN-TOTO | in-toto specifications | https://in-toto.io/docs/specs/ | Authorized supply-chain steps and verification |
| OPENTELEMETRY | OpenTelemetry | https://opentelemetry.io/docs/ | Traces, metrics, logs, execution lineage |
| JSON-SCHEMA | JSON Schema | https://json-schema.org/specification | Typed contracts for artifacts and evidence |
| PYTEST | pytest | https://docs.pytest.org/en/latest/reference/reference.html | Automated validation |

## MMI ingestion contract

For each source, preserve publisher, canonical URL, version/date, acquisition timestamp, artifact SHA-256 (only when an artifact was actually acquired), parser/version, parsable scope, component hierarchy, source and component depth through level 4, extracted observations, interpretations separately, corroborating sources, contradictions, unresolved gaps, uncertainty, and capability implications.

Keep protocol completeness independent from knowledge completeness. Distinguish discovery from acquisition. Barrot-generated material is not independent corroboration. Do not claim full ingestion from a manifest or summary alone. Record blocked/unparsed scope rather than fabricating it.
