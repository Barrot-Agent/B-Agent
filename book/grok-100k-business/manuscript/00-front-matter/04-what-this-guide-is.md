# What This Guide Is (And What It Will Make You Build)

This is a build manual for a one-person company that runs on agents. It has one
architecture, five employee blueprints, one product thesis, and one operating
system. By the last page you should have a working employee, a price, a fence, and
a number you can defend.

## The architecture: GrokBot OS

The name is used throughout as shorthand for six layers, in dependency order.
Every chapter maps to one of them.

| Layer | What it is | Where it lives |
|---|---|---|
| **1. Brain** | The model that plans, writes and decides | Grok Bot, Grok 4.7, `grok-build-0.1` |
| **2. Hands** | A real computer: browser, filesystem, terminal | Grok Bot's cloud computer; Grok Build's TUI, headless mode, ACP |
| **3. Skills** | Written procedures that encode how your best work is done | Grok Bot skills and routines; Grok Build skills and plugins |
| **4. Connectors** | Access to the systems that hold the truth | MCP servers and plain APIs |
| **5. Swarm** | More than one agent, handing work off | Multi-bot teams; multi-agent models |
| **6. Fence** | Memory, approvals, budgets, rollback | Approvals, sandboxing, ledgers, your own rules |

Parts Two and Five are the OS. Parts Three and Four are what you sell once the OS
holds.

## The evidence standard

Three kinds of statements appear in this book, and they are labeled differently.

1. **Documented.** A capability, limit or price that appears on the vendor's own
   documentation. These were checked on 2026-11-17 and the pages are listed in
   Appendix F. Prices change; the arithmetic method does not.
2. **Measured.** A number produced by running code — a test count, a latency, an
   error rate, a cost from an actual invoice. Every measured number in this book
   came from a repository you can re-run.
3. **Assumed.** An input you must supply: your price, your conversion rate, your
   hours saved. Assumptions are written as assumptions and carry a sensitivity
   table, because a single-point forecast is a lie with a decimal.

If a claim is not labeled, treat it as an assumption and check it before you bet
money on it.

## What this guide will not do

It will not give you a market. It will not make a bad offer good. It will not
promise that an agent's output is correct — Chapter 28 exists because it is not.
It will not tell you to fire anyone. And it will not pretend that autonomy without
approval is a feature; in every system described here, the agent proposes and the
operator disposes.

## What you will have built

- One employee that does a job you currently pay a human for, end to end.
- A written job description for it, precise enough to test.
- A connector set — the minimum number of systems it needs, not the maximum.
- An approval matrix that names what it may never do alone.
- A cost model per delivered unit, with a floor price.
- A monitoring loop that catches the failure you already know it will make.
- A price and a delivery promise you can put in front of a stranger.

That is the whole book. Everything else is detail and evidence.
