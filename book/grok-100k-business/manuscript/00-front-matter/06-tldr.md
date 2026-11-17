# The TLDR: A $100K/Month Company in One Page

**The model.** You sell a finished job, not an agent. A customer pays a monthly
fee for an output that a person used to produce: qualified meetings, research
memos, published content, reconciled books, cleaned operations queues. Agents
produce the output. You handle exceptions, relationships and quality.

**The arithmetic.** $100K/month is one of these:

| Customers | Price/month | Revenue | Who this is for |
|---:|---:|---:|---|
| 50 | $2,000 | $100,000 | small businesses, one deliverable each |
| 20 | $5,000 | $100,000 | mid-market, a department-level output |
| 5 | $20,000 | $100,000 | agencies and funds buying a function |

Pick the row that matches the buyer you can actually reach. Most first-time
operators should start at the bottom row and work down, because five buyers is a
sales problem you can solve by hand.

**The cost.** Documented Grok pricing at the time of writing: $2 per million input
tokens, $6 per million output tokens for `grok-4.7` under 200K prompt tokens.
A 12,000-token job with a 2,000-token answer costs about four cents. Even at ten
times that volume with retries, tool calls and a reviewer pass, inference is cents
per deliverable. **Model cost is not what makes this business hard.** Acquisition,
quality control and exception handling are.

**The first employee.** The most expensive repetitive job you can describe in
writing, with a sample of good output and a sample of bad output. Not the easiest
job. The most expensive one.

**The fence.** Four rules, written before the agent runs: what it may do alone,
what it must ask for, what it may never touch, and what happens when it is wrong.
Money movement, customer-facing sends, deletions and credential changes sit behind
approval. Everything else runs.

**The loop.** Build one employee, measure its error rate on 50 real items, price
the job at 3–5× your fully loaded cost, deliver for one customer, then hire the
second agent with the money from the first.

**The failure mode.** Automating a job you cannot define, granting access you
cannot revoke, and discovering the error rate from a customer instead of a test.
Chapters 12 and 28 exist to prevent exactly that.
