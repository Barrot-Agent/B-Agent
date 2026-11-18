# SANDBOX TRADING — PAPER ONLY

**PAPER ONLY. NO REAL MONEY. SANDBOX ACTIVE.**

No wallet. No seed phrase. No exchange account. No API key. No order path.
Starting paper balance: **10,000 USDT (fake)**.

The engine is `barrot_agent/trading/paper_sandbox.py`. It imports no network
library and builds no client. A test parses the module's imports and fails if
anything in `{socket, ssl, http, urllib, requests, aiohttp, httpx, websocket,
websockets, ccxt, web3}` appears. If an exchange credential is present in the
environment, the CLI aborts before evaluating anything.

Run:

```bash
python scripts/paper_trade.py demo     # evaluate the 3 fixtures -> PAPER_TRADES.csv
python scripts/paper_trade.py report   # win rate, avg R, drawdown, mistakes
python -m pytest tests/test_paper_sandbox.py -q
```

---

## 0. Hard stop rules

1. No real money, ever, in this mode. Not a test order, not a dust amount.
2. No seed phrase, private key, or exchange credential is requested, stored, or
   accepted. If one is pasted, it is not used; the run aborts.
3. If any step would need a live venue, the run stops and returns here.
4. Every price in this file is **SIMULATED**. There is no market feed in this
   runtime. Prices exist so the arithmetic can be checked, not to express a view.
5. A trade with an unverified contract, an unknown news state, or a missing stop
   cannot be promoted out of paper. Unknown is a reject, not a pass.

## 1. Transmuted learning plan

My version of the brief. Each domain has a mastery test that is an artefact, not
a feeling. Mastery means the test runs and passes.

### D1 — Blockchain mechanics

Mastery test: produce a settlement table for BTC, ETH, Arbitrum, Base, Solana
that names, per chain, the ordering mechanism, what "final" means, and what a
reorg costs the trader.

Mechanisms to hold:

- **Block and hash.** A block commits to its parent hash; changing history means
  redoing work or breaking the validator set's agreement.
- **UTXO vs account.** BTC tracks unspent outputs; ETH tracks balances and nonces.
  Consequence: BTC fee = sat/vB against input/output weight; ETH fee = gas units
  x (base fee + priority) under EIP-1559.
- **PoW vs PoS.** BTC is PoW, probabilistic finality measured in confirmations.
  ETH is PoS since the Merge; finality comes from Casper FFG checkpoints, about
  two epochs (an epoch is 32 slots at 12 s, so roughly 12.8 minutes).
- **Forks and reorgs.** A reorg rewrites recent history. Exchanges credit
  deposits after a confirmation depth for this reason. A trader's risk is a fill
  that later did not exist.
- **L2 ≠ L1.** Correction to the brief: **Solana is a separate L1, not an
  Ethereum L2.** Arbitrum is an optimistic rollup (withdrawal to L1 waits out the
  challenge window); Base is an OP Stack optimistic rollup. Both inherit Ethereum
  settlement, neither removes the bridge risk.
- **Wallets.** Hot = key on a networked device. Cold = key offline. Address
  derivation comes from the seed; that is exactly why the seed is the asset and
  never an input to any tool here.

Unverified numbers: TPS, median fees, and bridge wait times are venue- and
load-dependent. They are **UNVERIFIED** in this document and may not be quoted as
fact without a dated source.

### D2 — Smart contracts

Mastery test: audit one real token contract on Basescan and return
PASS / FAIL / UNKNOWN per checklist line in section 2, with the function name and
the line of source for every finding.

Mechanisms to hold:

- **Standards.** ERC-20 = fungible balances plus `approve`/`transferFrom`.
  ERC-721 = unique ids. ERC-1155 = multi-token in one contract.
- **Approve/allowance.** An unlimited approval lets the spender move the balance
  later. Revoke or bound it. This is the most common drain path.
- **Reentrancy.** An external call before the state update lets the callee
  re-enter. Defence: checks-effects-interactions, plus a reentrancy guard.
- **Slippage and MEV.** A sandwich needs a victim with a wide tolerance. Bound
  slippage; a failed transaction is cheaper than a drained one.
- **Honeypot.** Sells revert while buys succeed: blacklist, cooldown, max-tx,
  trading toggle, fee that exceeds the balance.
- **Rug vectors.** Mint authority, owner pause, upgradeable proxy, fee setter,
  liquidity removal, holder concentration.
- **Verified vs unverified.** Verified means the published source compiles to the
  deployed bytecode. Unverified is not proof of fraud, but it is unauditable, so
  the checklist returns UNKNOWN and the trade is blocked.

### D3 — Cryptocurrency market structure

Mastery test: given a token, produce supply, circulating supply, FDV, unlock
schedule next 12 months, and the venue type, each with a source and date.

Mechanisms to hold:

- **Spot vs perpetual.** Spot settles an asset. A perp is a derivative with
  funding, no expiry, and a liquidation price. Funding is a periodic payment
  between longs and shorts, not a fee to the venue.
- **Leverage and liquidation.** Liquidation happens when equity falls below
  maintenance margin. Leverage moves the liquidation price toward entry; a 1%
  stop and 20x leverage are incompatible.
- **Stablecoins.** USDT (Tether) and USDC (Circle) are issuer liabilities
  supported by attestations; DAI is overcollateralised crypto debt. All can
  depeg. In this sandbox the quote asset is USDT, so a USDT depeg hits every
  balance at once. That risk is stated, not hedged.
- **Tokenomics.** Market cap = price x circulating supply. FDV = price x max
  supply. Unlocks add sellable supply; vesting schedules say when.
- **CEX vs DEX.** A CEX matches an order book. A DEX prices an AMM curve; the LP
  earns fees and carries impermanent loss when the ratio moves.

### D4 — Day trading, as a risk discipline

Mastery test: 20 logged paper trades, each with entry, stop, target, thesis,
outcome, R, and mistake tag, plus the report in section 6.

Mechanisms to hold:

- **Structure.** Support/resistance, trend, and volume define where a stop can
  live. An indicator that is not used to place the stop is decoration.
- **VWAP, RSI, MACD, EMA 9/21/50/200, volume profile.** Each answers one
  question: value (VWAP), momentum exhaustion (RSI), momentum change (MACD),
  trend state (EMA stack), participation (volume profile). None is a signal on
  its own.
- **Risk first.** 1% max risk per trade, 2R minimum, stop always, 3 trades a day,
  no revenge trading. Position size is an output of the stop, never an input.
- **Sessions.** London and New York opens cluster liquidity; high-impact news
  widens spreads and gaps stops. Offline, the news state is UNKNOWN, which is
  recorded rather than guessed.
- **Journal.** Every trade needs entry, exit, thesis, R, mistake tag. A trade
  without a thesis cannot be reviewed and therefore cannot teach anything.

## 2. Contract red-flag checklist

Run before any paper trade. Any FAIL blocks. Any UNKNOWN blocks. There is no
"probably fine". Native assets return `N/A_NATIVE` with that reason written down.

| # | Check | PASS looks like | FAIL / UNKNOWN means |
|---|---|---|---|
| 1 | Source verified on the explorer | source compiles to deployed bytecode | unverified: unauditable, blocked |
| 2 | Owner privileges | renounced or timelocked, no pause/blacklist | live mint, pause, blacklist, or fee setter |
| 3 | Mint authority | fixed supply, no mint function | unlimited or owner-callable mint |
| 4 | Upgradeability | immutable contract | proxy with an upgrade admin |
| 5 | Sell path | a small sell succeeds on a fork or test | revert, cooldown, max-tx, or fee > proceeds |
| 6 | Liquidity | locked, known locker, unlock date published | unlocked or unknown unlock date |
| 7 | Holder concentration | top 10 wallets reasonable, no deployer cluster | one wallet holds supply or deployer-linked set |
| 8 | Tax / fee changes | fixed and bounded | owner can change tax at will |
| 9 | Proxy / admin key | none, or multisig + timelock | single EOA admin |
| 10 | Provenance | audit published and current | no audit, or audit predates a code change |

## 3. Sandbox contract

| Item | Value |
|---|---|
| Balance | 10,000 USDT (fake) |
| Risk per trade | <= 1.0% = <= 100 USDT |
| Minimum reward/risk | 2.0R |
| Stop | mandatory, correct side of entry |
| Max trades per day | 3 |
| Leverage | none — notional must not exceed balance (BARROT-ADDED) |
| News state | HIGH_IMPACT rejects; UNKNOWN records and stays in paper |
| Contract verdict | PASS or N/A_NATIVE only |

Sizing, in order: `risk_amount = balance x risk_pct`; `stop_distance = |entry -
stop|`; `units = risk_amount / stop_distance`; `notional = units x entry`;
`leverage = notional / balance`. Every one of those fields is written to the CSV
so the arithmetic can be re-checked without trusting the engine.

## 4. First 3 paper setups

All prices are simulated fixtures. `data_source=SIMULATED_NO_FEED` on every row.
Nothing here is a market view.

| Id | Pair | Side | Entry | Stop | Target | Stop % | Risk | Units | Notional | Lev | R | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P-001 | BTC/USDT | long | 62,000 | 61,250 | 63,500 | 1.21% | 100 | 0.13333333 | 8,266.67 | 0.83x | 2.00 | ACCEPT |
| P-002 | ETH/USDT | long | 3,050 | 2,980 | 3,155 | 2.30% | 100 | 1.42857143 | 4,357.14 | 0.44x | 1.50 | REJECT — below 2R |
| P-003 | SOL/USDT | long | 142.50 | 138.90 | 149.70 | 2.53% | 100 | 27.77777778 | 3,958.33 | 0.40x | 2.00 | ACCEPT |

Balance before each: 10,000.00. Neither accepted trade is closed, so balance
after equals balance before; no PnL is booked and no win rate exists yet. The
ETH row is kept on purpose: it is the negative control that proves the 2R rule
actually rejects.

Daily cap use: 2 of 3. A fourth setup would be rejected by the same function.

## 5. The loop

1. Pick BTC/USDT, ETH/USDT, SOL/USDT.
2. Describe 1h, 15m, 5m structure. **Every price must have a provenance tag:**
   `SEAN_SUPPLIED`, `SIMULATED`, or a dated feed. No provenance, no trade.
3. Run the checklist (section 2) and the risk gate (section 3).
4. If approved, log it with the sizing arithmetic. If rejected, log the reason.
5. After 20 trades, produce the section 6 report, then change exactly one rule.
6. Repeat. A rule change requires the before/after numbers, or it is not a change.

## 6. Report after 20 trades

| Metric | Definition |
|---|---|
| Win rate | winning closed trades / closed trades |
| Avg R | mean realised R over closed trades |
| Max drawdown | largest peak-to-trough fall in the paper equity curve |
| Top 3 mistakes | most frequent mistake tags, with counts |
| Rule to fix | exactly one, with the evidence that produced it |

`python scripts/paper_trade.py report` computes the first four from the CSV.

## 7. What is not proven

- No market data was ingested. No feed is connected. Prices are fixtures.
- No edge is claimed. Zero closed trades means zero measured performance.
- No contract was audited. The checklist is ready; it has not been run on a real
  token, so its first real use is still a test.
- Win rate, average R, and drawdown are implemented and unit-tested on synthetic
  rows only. They describe the arithmetic, not a strategy.
- USDT depeg risk is stated, not hedged.

## 8. Status

- Mode: PAPER ONLY
- Real money at risk: 0
- Live credentials in environment: none at run time (checked before every run)
- Network imports in the engine: none (enforced by test)
- Trades evaluated: 3 (2 accepted, 1 rejected)
- Closed trades: 0
- Ledger: `PAPER_TRADES.csv`
- Verification: `tests/test_paper_sandbox.py` — 22 tests
