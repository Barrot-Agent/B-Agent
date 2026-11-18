# XRP PLAYBOOK

Rules added only after a cycle measured them. A rule that
fails gets removed in a later cycle, not quietly ignored.

## Cycle 0 — graded at live-20261118T193754
- Focus USDT; accepted 2, rejected 7, closed 0.
- Refused-rotation cost: BTC -0.34%, ETH -0.44%, SOL -0.37%, USDT +0.34%, XLM +0.07%.
- Evidence: USDT refused, would have returned +0.34% after costs.
- **Rule added:** A missing input is not neutral. An UNKNOWN field forced a refusal on USDT that cost +0.34% at the next snapshot. Treat a missing field as a request for data, not as a decision.
- Rule removed or fixed: none — this is the first graded cycle.
