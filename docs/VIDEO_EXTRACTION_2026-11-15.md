# Video Extraction — 2026-11-15

Extraction of two YouTube sources into Barrot's framework. Facts are separated from
claims: every number below is attributed either to the video, to the primary source
(repo/paper/leaderboard), or to Barrot's own measurement.

## Sources and method

| # | Video (published title) | Channel | Video ID | Published | Length |
|---|---|---|---|---|---|
| 1 | "Did Stanford Just Solve AI Memory? (Memorilla)" | Better Stack | `lNpDxKfBlf8` | 2026-11-15 | 11:20 |
| 2 | "It's Official: We've Entered AGI" | Julia McCoy | `us_pnC6ETNA` | 2026-11-15 | 14:09 |

- URLs: https://www.youtube.com/watch?v=lNpDxKfBlf8 · https://www.youtube.com/watch?v=us_pnC6ETNA
- Transcripts: full English captions fetched with `youtube-transcript-api` (293 and 325
  segments, 11,137 and 11,704 characters). No transcript was invented; caption punctuation
  is imperfect, so quotes below are lightly normalised.
- Video 1 title differs from the brief's wording ("Stanford Squeezed a Whole Book Into 16
  Tokens" is the same story, but the published title is the one above).
- Primary sources used to check video 1:
  - Paper: https://arxiv.org/abs/2610.21375
  - Code: https://github.com/snap-stanford/memorilla
  - Project page: https://memory.stanford.edu
  - Checkpoints: https://huggingface.co/memorilla/Memorilla-Qwen3-8B
  - Independent tests by the video author: https://github.com/andrisgauracs/memorilla-demos
- Primary source used to check video 2:
  - ARC Prize, "GPT-6 Astra on ARC-AGI-3", 2026-09-03: https://arcprize.org/blog/astra
  - Leaderboard: https://arcprize.org/leaderboard

---

## Video 1 — Memorilla (Stanford): 16 memory tokens

### What it is

A memory system for a **frozen** LLM. It reads an entire document collection (chat history,
book, movie script) and hands the decoder a **fixed 16 memory tokens**, query-dependent,
instead of the documents. The decoder never grows its context with collection size.

### Mechanism (video + repo code)

1. **Encode once.** Every document is embedded into one vector with
   `Qwen3-Embedding-4B`. Embeddings are reused across questions.
2. **16 learned slots.** A small `MemoryModule` (~200M parameters by the video's count;
   repo config: 16 memories, 8 heads, 0 self-attention layers, 2 cross-attention layers,
   dropout 0.1) starts from 16 query vectors.
3. **Query-conditioned retrieval inside the module.** Each slot scores every document
   vector against the question, then blends the documents weighted by relevance. Two
   cross-attention passes: the second refines what the first selected.
4. **Projection into the decoder.** The 16 vectors are projected into Qwen3-8B's input
   embedding space and inserted where normal word embeddings would go. **Decoder stays
   frozen.**
5. **Training only the module**, in three stages (from `configs/`):
   - Stage 1 `stage1_enwiki.yaml`: reconstruct ~2M Wikipedia passages, lr 3e-4, 1 epoch,
     4 GPUs, max length 1024.
   - Stage 2 `stage2_mixture.yaml`: SQuAD v2, DROP, CoQA, PubMedQA, QuAIL, PWC, CNN/DM,
     SAMSum, DialogSum, MS MARCO; same lr, 1 epoch.
   - Stage 3 `stage3_multitask.yaml`: all eight eval benchmarks (PV4, PersonaMem-v2,
     FactKG, TriviaQA, NarrativeQA, PubMedQA, LAMP-4, LAMP-7), lr 1e-4, 5 epochs,
     max length 2048.
   - Cost per README: ~19 hours on 4×H100 80GB, ~310 GiB of data/embeddings.
6. **Optional memory cache** (repo): keys/values of the cross-attention layers are
   computed once per collection. Question latency drops from 74 ms to 8.1 ms for 1M
   documents (5.0 ms with `torch.compile`), at 4× the embedding memory (80 GiB for 4M
   docs). Accuracy stays within 0.06 points of the default on FactKG.

Why 128k tokens become 16: the 128k tokens are embedded into ~512 document vectors
(512 × 250 tokens in the latency test). The memory module compresses *all* those vectors
into 16 output vectors, conditioned on the question. It is **not lossless compression** —
it is query-conditioned information selection with a hard output budget.

### Numbers: claim vs check

| Claim | Primary source | Independent test (video) | Verdict |
|---|---|---|---|
| 107 chats (~32k tokens) → 16 tokens (~2,000× fewer) | README example | README example reproduced almost word for word | confirmed |
| 512 docs (~128k tokens): 0.74 s vs 19.9 s full context (27× faster) | README/paper, 1×H100 | Model time flat at ~0.12 s; **3.2 s including embedding**, ~6× faster than 19.3 s | speed claim **partially** holds |
| FactKG 84.33% vs 80.43% full-context, 108× fewer tokens | paper/README | not tested | unverified independently |
| NarrativeQA compression >4,000× | README/paper | not tested | unverified independently |
| TextWorld agent success 18.6% → 24.2% | paper/README | not tested | unverified independently |
| Best average on 5 of 8 benchmarks vs Mem0 / MemoRAG | paper/README | not tested | unverified independently |

### Failure modes observed (these matter more than the headline)

- **Buried-clue test** (150 synthetic chats, hidden facts unrelated to the question):
  none of the four methods found a buried clue. RAG got the easy control question
  (sister's name/birthday). Full context mostly refused. **Memorilla hallucinated**: invented
  a shellfish allergy, and gave the wrong sister name and birthday.
- **Detail decay**: with only the one sister chat, the name was right but the birthday was
  wrong; adding more chats erased the name too.
- **Book test** (*The Hound of the Baskervilles*, ~72k tokens, exceeds Qwen3-8B's normal
  window): full context 5/8 plot questions (it only saw the second half), RAG 4/8,
  **Memorilla 1/8**; it attributed a letter to a character from a different Holmes story.
- **Interpretation**: a whole chat squeezed into one vector keeps the *gist*, loses exact
  names/dates, and fills gaps with plausible inventions. Works best on data resembling its
  training mix; the repo allows retraining on your own data without code changes.

### Setup, prompts, code

Environment: Linux + CUDA, Python 3.11, 80 GB GPU, ~25 GB model download, vLLM.
Encoder `Qwen3-Embedding-4B`, decoder `Qwen3-8B` (both frozen).

```bash
git clone https://github.com/snap-stanford/memorilla.git
cd memorilla
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -e .
uv pip install --no-build-isolation flash-attn==2.7.4.post1
```

```python
from memorilla.benchmarks import PERSONA_PROMPT
from memorilla.data import ensure_data, load_split
from memorilla.vllm import MemoryVLLM

row = load_split("pmv2", "test", ensure_data("pmv2", ["test"]))[73]
model = MemoryVLLM.from_pretrained("memorilla/Memorilla-Qwen3-8B", "pmv2")
answer = model.answer(row["question"], row["documents"], system_prompt=PERSONA_PROMPT)
```

Prompts used by the repo (verbatim, `memorilla/benchmarks.py`):

- `PERSONA_PROMPT`: "You are a personalized AI assistant. Answer the question about the
  user based on your understanding of the user."
- `FACT_CHECK_PROMPT`: "You are a fact-verification assistant. Decide whether the given
  claim is true or false based on your knowledge. Output exactly 'True' or 'False' with no
  other text."
- `BRIEF_ANSWER_PROMPT`: "You are a question-answering assistant. Provide a direct, brief
  answer in 1-2 sentences. Do not include preamble, context, or explanation."

### Rules Barrot takes from this

1. Fixed memory budget, always: memory cost must not scale with history length.
2. Query-condition the memory; the same history produces different gists per question.
3. Two passes beat one: select, then refine from the first selection.
4. A gist is for *context and preferences*; exact names, numbers and dates need a raw
   retrieval fallback (RAG) — the video's own tests show the gist alone invents them.
5. Never let a summariser write facts: extract verbatim spans and keep the source pointer.

---

## Video 2 — "It's Official: We've Entered AGI" (Julia McCoy)

### Claims, checked

| Claim in video | Check | Status |
|---|---|---|
| ARC-AGI-3: humans solve 100%, frontier models <1% at launch | ARC Prize pages confirm the design and the human baseline | verified |
| "GPT-5 Astra" scored 99.9% on ARC-AGI-3 (OpenAI's own harness) and 62.7% on ARC's neutral setup | Official post is **GPT-6 Astra**: 99.9% with the Provider Adapter harness at `high`, 62.7% with the Standard harness at `max` | verified, with a name error in the video |
| Astra used fewer actions than the median human on 96% of levels, about half the actions on average | ARC Prize post states exactly this | verified |
| Astra invented its own shorthand notation and built custom tools (maze solver, guard tracker) | ARC Prize analysis section describes both | verified |
| "AGI is here" | ARC Prize explicitly says the result is **not** proof of AGI: closed rule-based games, real world messier, next test already being built | overclaim / hype |
| GPT-5.6 Soul 7.78% (July), GPT-6.1 Soul 96.4% at 77% lower cost (Sep 30) | Not found in the ARC leaderboard/blog excerpt checked here | unverified |
| METR: 4-minute tasks (GPT-4, 2023) → 16-hour tasks (Claude Mythos preview, 2026) | Not checked in this pass | unverified |
| "Whistleblower psyop": funding via Survival and Flourishing Fund, specific grant amounts | Names/amounts are checkable claims; the intent ("built to make you afraid") is opinion | partially checkable, interpretive |
| Productivity anecdotes (Stripe, DataCamp, Mollick, 25h/30k LOC Codex run) | Single-source anecdotes, not reproduced here | unverified |

The one number worth keeping is the pair **62.7 vs 99.9 on the same model**: the
difference is the harness (persistent reasoning state + compaction vs carrying notes), not
a better model. That is the video's own "fine print", and it is the actionable part.

### Prompt pattern for long-running work (verbatim shape)

1. Clear finish line — what "done" looks like, which pages, how you will know it works.
2. Permission to check its own work — test, find what broke, fix it, keep going.
3. A memory file — `progress.md` with finished work, next step, decisions made.
4. Room to run — do not approve every step.
5. Stop only for something it truly cannot decide.

This matches Barrot's existing loop (memory file + validation + ship loop); it is recorded
here as the external confirmation, not as a new mechanism.

### Hype filter applied

- Check the benchmark's own caveat before the speaker's framing.
- Check the harness (standard vs provider adapter) before comparing scores.
- Check cost and token budget, not just accuracy.
- Separate "funding is real" from "intent is proven".
- Ask who benefits from the emotional framing.

---

## What was implemented in Barrot

New module: `barrot_agent/gist_memory.py`.

| Memorilla element | Barrot implementation (CPU, stdlib) |
|---|---|
| 16 latent memory tokens | 16 gist slots, each a verbatim phrase (default budget 16 × 6 words) |
| Query-conditioned slots | IDF-weighted query overlap + precision bonus |
| Two cross-attention passes | Two selection passes; pass 2 adds terms found by pass 1 |
| Blend of relevant documents | Maximal-marginal-relevance selection with redundancy penalty |
| Frozen decoder | Prompt block via `to_prompt()`; the 0.5B model is never modified |
| Loses exact facts | Extractive only; `expand()` returns the full source clause for RAG fallback |
| Trained module | No training, no embeddings, no GPU — deterministic and offline |

API:

```python
from barrot_agent.gist_memory import compress_documents

result = compress_documents(documents, "What should I cook given my health history?")
result.render()       # "- family history of type 2 diabetes\n- ..."
result.to_prompt()    # prompt block with an anti-invention rule
result.expand(0)      # verbatim source clause behind token 0
result.as_dict()      # JSON-safe, for offline memory files
```

Tests: `tests/test_gist_memory.py` — 14 tests, all passing (`python -m pytest
tests/test_gist_memory.py --no-cov`). Lint: `python -m flake8` clean on both new files.

Deliberately **not** implemented: latent token training, Qwen3-8B/vLLM inference, embedding
encoding, the Memorilla cache. Those need CUDA and 80 GB of GPU memory, which Termux does
not have, and cloning the repo does not make Barrot's 0.5B model stronger.

Limits stated honestly: the compressor is lexical. It cannot match "health issues" to
"diabetes" without a shared term; it preserves rare terms and numbers, not synonyms. Pair
it with the raw source when the answer must be exact.

## Links

- Memorilla paper — https://arxiv.org/abs/2610.21375
- Memorilla code — https://github.com/snap-stanford/memorilla
- Memorilla project — https://memory.stanford.edu
- Memorilla checkpoints — https://huggingface.co/memorilla/Memorilla-Qwen3-8B
- Independent tests — https://github.com/andrisgauracs/memorilla-demos
- ARC Prize Astra post — https://arcprize.org/blog/astra
- ARC Prize leaderboard — https://arcprize.org/leaderboard
- Video 1 — https://www.youtube.com/watch?v=lNpDxKfBlf8
- Video 2 — https://www.youtube.com/watch?v=us_pnC6ETNA
