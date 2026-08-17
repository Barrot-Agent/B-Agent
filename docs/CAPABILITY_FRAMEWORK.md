# Governed Capability Framework

Barrot's capability framework is intentionally model-agnostic. It inventories
the existing subsystems, routes work to compatible providers, and evaluates
candidate outputs before selecting one; it does not copy proprietary model
weights or training data.

`barrot_agent.capability_framework` provides:

- a taxonomy for reasoning, coding, vision, audio, research, planning, and tool
  use;
- repeatable benchmark cases and explicit score thresholds;
- provenance and license checks, output/prompt resource limits, and candidate
  caps;
- an append-only continual-learning store for feedback, versioned proposals,
  human approval, and rollback;
- promotion gates requiring both safety and regression scores.

Existing MCP approval, provenance, and sandbox modules remain the enforcement
boundary for tool integrations. A production deployment should connect their
reports to `Evaluation` rather than allowing a learning proposal to mutate
code directly.
