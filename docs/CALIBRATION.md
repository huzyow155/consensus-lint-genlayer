# ConsensusLint Calibration & Empirical Measurements

Calibrated against regression rule fixtures, real-world historical Intelligent Contracts on GenLayer Studionet (Preview), public reference examples, and manual precision reviews.

## (a) & (b) Rule Fixtures Precision and Recall (Author-Written Regression Suite, n=72 snippets)

| Rule | Name | Severity | Method | Pass Fixtures | Fail Fixtures | Precision | Recall | Evidence Type |
|---|---|---|---|---|---|---|---|---|
| `CL01` | Missing or invalid version header | MINOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL02` | Missing or invalid py-genlayer dependency pin | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL03` | Non-ASCII characters in contract source | MINOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL04` | Not a GenLayer contract class | INFO | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL05` | TreeMap assignment in __init__ | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL06` | Unbounded list load-append-store pattern in write method | MINOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL07` | strict_eq used over dynamic payload or free-text | MAJOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL08` | Non-deterministic call outside consensus wrapper | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL09` | Validator does not recompute verdict or returns True unconditionally | CRITICAL | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL10` | Validator accesses leader calldata without gl.vm.Return check | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL11` | Validator waves through failures in except handler | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL12` | Silent default fallback on model parse failure | MAJOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL13` | Wall-clock time call used instead of chain clock | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL14` | Generic exception or assert used instead of gl.vm.UserError | MINOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL15` | URL validation by substring or prefix check without urllib.parse | MAJOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL16` | Unbounded string parameter in public write method | MINOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL17` | Unpaginated view method iterating collection | MINOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |
| `CL18` | Public parameter in prompt without visible sanitization | INFO | HEURISTIC | 2/2 | 2/2 | 100% | 100% | `LOCAL-ENGINE` |

## (c) Real-World Historical Contract Improvement Timeline & On-Chain Verification

Evaluates historical commits from prior Intelligent Contract repositories. Rows with `ON-CHAIN` evidence type were registered and audited directly on **GenLayer Studionet (Preview)** through ConsensusLint contract `0xE2cBaf1916Df7C742486B2eC4E5d3A3289115F2D`:

| Series | Version | Commit | SHA-256 | Evidence Type | Local Score | On-Chain Score | On-Chain Tx | Agreement | Delta vs Local |
|---|---|---|---|---|---|---|---|---|---|
| `CitationWatch` | v1.0.0 | `db7efa656f` | `e3b4bf9ce1...` | `ON-CHAIN` | 59 (D) | 52 | [`0xd8c25b2360...`](https://explorer-studio.genlayer.com/tx/0xd8c25b23605ecad62123691f58ed673e3fbb92285f8a84aa9cade2a73087565e) | `3/5` | -7 |
| `CitationWatch` | v1.1.0 | `fe0e1b82bf` | `130f8b11bf...` | `ON-CHAIN` | 83 (B) | 80 | [`0xa291cfde94...`](https://explorer-studio.genlayer.com/tx/0xa291cfde947bb2f9ad7db0a2253eba0a275143516b09142bddc1edebfce97292) | `3/5` | -3 |
| `CitationWatch` | v1.2.0 | `7726ce992f` | `d5598c5e11...` | `ON-CHAIN` | 80 (B) | 78 | [`0xe71a2a29fa...`](https://explorer-studio.genlayer.com/tx/0xe71a2a29fadf7e7fb2dea80285a68e2b6c2dc81fadcea7f3d72cc73a2bda97cd) | `3/5` | -2 |

### Target Provenance & Local Reproduction Commands

| Target | Repo | Commit | Relative File Path | Raw GitHub URL | Verification Command |
|---|---|---|---|---|---|
| `CitationWatch v1.0.0` | `huzyow155/citationwatch-genlayer` | `db7efa656f` | `contracts/SourceDriftLedger.py` | [Raw URL](https://raw.githubusercontent.com/huzyow155/citation-watch-genlayer/db7efa656f3ceb14d40b3607f1037fdcbcfdf6ef/contracts/SourceDriftLedger.py) | `git show db7efa656f:contracts/SourceDriftLedger.py | python scripts/tools/local_lint.py` |
| `CitationWatch v1.1.0` | `huzyow155/citationwatch-genlayer` | `fe0e1b82bf` | `contracts/SourceDriftLedger.py` | [Raw URL](https://raw.githubusercontent.com/huzyow155/citation-watch-genlayer/fe0e1b82bf9dc51b1dbb2c7ad61fc4cb3883971a/contracts/SourceDriftLedger.py) | `git show fe0e1b82bf:contracts/SourceDriftLedger.py | python scripts/tools/local_lint.py` |
| `CitationWatch v1.2.0` | `huzyow155/citationwatch-genlayer` | `7726ce992f` | `contracts/SourceDriftLedger.py` | [Raw URL](https://raw.githubusercontent.com/huzyow155/citation-watch-genlayer/7726ce992fd39ac1239165c02e527456f052a697/contracts/SourceDriftLedger.py) | `git show 7726ce992f:contracts/SourceDriftLedger.py | python scripts/tools/local_lint.py` |

## (d) Public GenLayer Examples (Neutral Reference Measurements)

*Note: Educational examples from `yeagerai/genlayer-simulator` pinned by commit `c94072951e483510329670aa427fba3fa6944f45` (`git cat-file -t` verified `commit`). Findings indicate conventions for this pinned rule catalogue and do not imply defects in production systems.*

| Contract | Commit | SHA-256 | Local Score | Grade | Findings Detected | Evidence Type |
|---|---|---|---|---|---|---|
| `storage.py` | `c94072951e` | `c19ffb3e0c...` | 94 | **A** | CL01 (1), CL16 (1) | `LOCAL-ENGINE` |
| `tip_jar.py` | `c94072951e` | `907d065882...` | 97 | **A** | CL01 (1) | `LOCAL-ENGINE` |
| `wizard_of_coin.py` | `c94072951e` | `339d88b142...` | 91 | **A** | CL01 (1), CL16 (1), CL14 (1), CL18 (1) | `LOCAL-ENGINE` |

### Public Examples Provenance & Fetch Commands

| Contract | Repo | Commit | Raw URL | Command |
|---|---|---|---|---|
| `storage.py` | `yeagerai/genlayer-simulator` | `c94072951e` | [GitHub Raw](https://raw.githubusercontent.com/yeagerai/genlayer-simulator/c94072951e483510329670aa427fba3fa6944f45/examples/contracts/storage.py) | `curl -s https://raw.githubusercontent.com/yeagerai/genlayer-simulator/c94072951e483510329670aa427fba3fa6944f45/examples/contracts/storage.py | python scripts/tools/local_lint.py` |
| `tip_jar.py` | `yeagerai/genlayer-simulator` | `c94072951e` | [GitHub Raw](https://raw.githubusercontent.com/yeagerai/genlayer-simulator/c94072951e483510329670aa427fba3fa6944f45/examples/contracts/tip_jar.py) | `curl -s https://raw.githubusercontent.com/yeagerai/genlayer-simulator/c94072951e483510329670aa427fba3fa6944f45/examples/contracts/tip_jar.py | python scripts/tools/local_lint.py` |
| `wizard_of_coin.py` | `yeagerai/genlayer-simulator` | `c94072951e` | [GitHub Raw](https://raw.githubusercontent.com/yeagerai/genlayer-simulator/c94072951e483510329670aa427fba3fa6944f45/examples/contracts/wizard_of_coin.py) | `curl -s https://raw.githubusercontent.com/yeagerai/genlayer-simulator/c94072951e483510329670aa427fba3fa6944f45/examples/contracts/wizard_of_coin.py | python scripts/tools/local_lint.py` |

## (e) Manual Precision Review (Self-Review, n=35, Four Rules)

- **Evidence Type**: `SELF-REVIEW`
- **Sample Size**: 25 non-INFO findings
- **Confirmed True Positives**: 25
- **Empirical Precision**: 100.0%

| Rule | Sampled | Confirmed | Unconfirmed | Empirical Precision | Evidence Type |
|---|---|---|---|---|---|
| `CL06` | 1 | 1 | 0 | 100% | `SELF-REVIEW` |
| `CL16` | 17 | 17 | 0 | 100% | `SELF-REVIEW` |
| `CL07` | 3 | 3 | 0 | 100% | `SELF-REVIEW` |
| `CL12` | 4 | 4 | 0 | 100% | `SELF-REVIEW` |

## (f) Bounded Model Layer Judgement Stability & On-Chain Observations

- **Labelled Code Excerpts**: 15
- **Standalone LLM Measurement**: `Not measured` (not measured in isolation (GenVM validator LLM model cannot be executed in standalone local script without GenVM sandbox or external API credentials; prompt parser and quote verification are unit-tested in tests/test_model_layer.py))
- **Unit Test Coverage**: Prompt templates, snippet clipping, JSON parser, and verbatim quote verification are unit-tested under `tests/test_model_layer.py` (all tests passing).
- **Safety Cap**: Model penalty is strictly capped at `20 points` (`MODEL_PENALTY_CAP`). Unverifiable quotes are downgraded to `UNCLEAR` (0 points penalty).

### Model Layer Observed Behaviour On-Chain

| Target | Question | Output Label | Quoted Verbatim Snippet | Quote Verified | Penalty | Assessment |
|---|---|---|---|---|---|---|
| GoodContract Fixture (2bac0b36b071) | `J2` | `FREE_TEXT_OR_PAYLOAD` | `return val_sand.calldata == ldata.get("sha256")` | `True` | -6 pts | Model false positive: comparing a deterministic SHA-256 string is a canonical bucket, but the model categorized it as FREE_TEXT_OR_PAYLOAD. |
| ConsensusLint Self-Lint (0xE2cBaf...) | `J3` | `NOT_ISOLATED` | `def prompt_call(): return gl.nondet.exec_prompt(prompt_text)` | `True` | -4 pts | Model cited the generic gl.nondet.exec_prompt call site rather than the prompt template assembly, resulting in 4 points penalty. |
