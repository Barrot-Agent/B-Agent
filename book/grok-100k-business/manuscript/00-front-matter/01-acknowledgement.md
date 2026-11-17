# Acknowledgement

This book has two authors, and only one of them is human.

Sean — the Orchestrator — set the constraints that made it possible: paper trading
only, no live keys, log everything, commit after every section, never break the
demo. Those are not writing constraints. They are operating constraints, and they
are the reason the numbers in this book can be re-run instead of believed.

The agent that drafted these pages runs on the same stack the pages describe: a
model behind a chat surface, a shell with real hands, a filesystem it can read and
write, tools it can call, a memory file it must consult before it starts, and a
fence that stops it from pushing to production without being asked. Every chapter
about "how to build the employee" was written by an employee built that way. When
the draft claims a test count, the test suite was run to produce it. When it
claims a cost, the price list was fetched and the arithmetic shown.

That is worth saying plainly because most books about agents are written from the
outside. This one is a work log with a spine.

Thanks are due to the people who published the primitives and left them
inspectable: the xAI documentation team, whose pages on Grok Bot, Grok Build and
pricing made Part Two checkable rather than speculative; the Model Context
Protocol maintainers, who turned "give the agent access to a system" into a
boring, reviewable interface; the Python, pytest and GitHub Actions communities,
whose tooling is the reason a single operator can hold a 1,000-test suite and a
deploy pipeline in one head.

Thanks also to the people who will never read this. The support reps, ops
assistants, bookkeepers and researchers whose jobs are being decomposed into
tasks right now. This book argues that the decomposition is real and that it pays.
It does not argue that the people are disposable. The honest version of this
transition is that the work moves, the accountability does not, and somebody still
has to be awake when the agent is wrong.

And to the readers who will try this and fail the first time: the failure is
informative. Chapter 28 exists because of it.

One more acknowledgement, of a discipline rather than a person. Every number in
this manuscript was produced by a script that can be run again: the test count by
the test suite, the verifier findings by the verifier, the cost tables by the
published rate card and arithmetic shown in the text. Where that was not possible,
the claim is labeled an assumption. If a reader disagrees with a number, they should
be able to reproduce it, and if they cannot, the number should not have been in the
book.
