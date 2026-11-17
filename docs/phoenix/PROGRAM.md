# Phoenix program: fiction mapped to utility

Date: 2026-11-17. Registry: config/phoenix_sources.json (12 sources, all probed
HTTP 200 today). Layers follow the fields contract: L1 established, L2 applied,
L3 speculative and labelled.

## Transmutation

ORIGINAL: "Pull data from every accessible known source, everything he needs to
learn to embody Phoenix from X-Men in the form of real world utility."

GAP 1: Phoenix is fiction. [FILLED GAP] There is no telepathy, no cosmic fire, no
resurrection. What exists is a set of engineering problems the character
dramatises: survive catastrophic energy and heat, recover after total loss, act in
parallel, and return changed. Those are buildable.

GAP 2: "Every accessible source" is not "the internet". [FILLED GAP] It is the
twelve public APIs probed today. Crawling beyond their terms is a legal and cost
risk, not a capability.

GAP 3: No success measure. [FILLED GAP] Each cluster below has one number that
decides whether it is real.

TRANSMUTED: "Map Phoenix traits to engineering capabilities, pick sources that can
evidence each one, probe those sources and record status, define one measurable
KPI per capability, and do not claim any capability until its KPI is measured."

## Trait to capability map

| Fiction trait | Real capability | Layer | KPI |
|---|---|---|---|
| Firebird rebirth | recovery from total loss | L2 | restore drill time; data loss zero |
| Cosmic fire | thermal and energy handling | L1 | watts dissipated per unit volume under load |
| Telepathy | shared state between agents | L2 | convergence time between two replicas |
| Telekinesis | actuation and orchestration | L2 | task completion rate without a human |
| Immortality | durability and redundancy | L1 | survival of N-1 failure |
| Transformation | postmortem to promotion loop | L2 | defects closed per cycle, repeat rate |

## Six clusters and what evidence each needs

1. Recovery. Sources: cisa_kev, nvd, github. Test: destroy a service, restore from
   backup, measure. KPI: restore time and zero data loss.
2. Thermal and energy. Sources: arxiv, nasa, worldbank. Test: thermal budget for a
   load, with numbers. KPI: watts per unit volume, measured not asserted.
3. Redundancy and consensus. Sources: github, arxiv. Test: kill one replica, check
   quorum behaviour. KPI: availability during N-1.
4. Parallel agents. Sources: docs_xai, huggingface. Test: two agents on one task,
   measure convergence. KPI: convergence time, cost per task.
5. Learning loop. Sources: openalex, crossref, pubmed. Test: claim arrives with a
   source; verify against a second source. KPI: retraction catch rate.
6. Governance. Sources: nvd, cisa_kev, internal flight recorder. Test: every
   promotion has an approval and a receipt. KPI: promotions without evidence,
   target zero.

## What is not claimed

- No telepathy. Shared state is a database and a protocol, not a mind.
- No resurrection. Rollback restores a copy; it does not restore lost writes.
- No cosmic fire. Plasma and thermal systems are real, measured, and expensive.
- No capability is "learned" until its KPI is measured. Reading the sources is
  orientation, not capability.

## What is running right now

Probing only. The registry records 12 reachable sources with license and teaching
value. No crawl, no bulk download, no ingestion loop has been started, because
each source needs a purpose and a rate-limit budget before it is worth the wall
clock. That is the next gate, and it is deliberate.

## Honest boundary

"Simultaneously and dynamically identify and pull from every accessible source" is
an unbounded instruction. The bound used here: twelve probed APIs, read-only,
license recorded, one KPI per cluster, no claim without a measurement. If you want
the ingestion loop switched on, the decision needed is which KPI matters first,
because that decides which source is worth its rate limit.
