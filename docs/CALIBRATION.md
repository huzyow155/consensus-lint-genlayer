# ConsensusLint Calibration & Empirical Measurements

Calibrated against rule fixtures, local and on-chain reference implementations, historical Intelligent Contracts, and public GenLayer example contracts.

## (a) & (b) Rule Fixtures Precision and Recall

| Rule | Name | Severity | Method | Pass Fixtures | Fail Fixtures | Precision | Recall |
|---|---|---|---|---|---|---|---|
| `CL01` | Missing or invalid version header | MINOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL02` | Missing or invalid py-genlayer dependency pin | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL03` | Non-ASCII characters in contract source | MINOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL04` | Not a GenLayer contract class | INFO | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL05` | TreeMap assignment in __init__ | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL06` | Unbounded list load-append-store pattern in write method | MINOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% |
| `CL07` | strict_eq used over dynamic payload or free-text | MAJOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% |
| `CL08` | Non-deterministic call outside consensus wrapper | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL09` | Validator does not recompute verdict or returns True unconditionally | CRITICAL | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL10` | Validator accesses leader calldata without gl.vm.Return check | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL11` | Validator waves through failures in except handler | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL12` | Silent default fallback on model parse failure | MAJOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% |
| `CL13` | Wall-clock time call used instead of chain clock | MAJOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL14` | Generic exception or assert used instead of gl.vm.UserError | MINOR | STRUCTURAL | 2/2 | 2/2 | 100% | 100% |
| `CL15` | URL validation by substring or prefix check without urllib.parse | MAJOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% |
| `CL16` | Unbounded string parameter in public write method | MINOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% |
| `CL17` | Unpaginated view method iterating collection | MINOR | HEURISTIC | 2/2 | 2/2 | 100% | 100% |
| `CL18` | Public parameter in prompt without visible sanitization | INFO | HEURISTIC | 2/2 | 2/2 | 100% | 100% |

## (c) Real-World Historical Contract Improvement Timeline

Measured historical commits from real project repositories on GenLayer Studionet (Preview):

| Series | Version | Commit | Score | Grade | Key Findings |
|---|---|---|---|---|---|
| `CommitmentLedger` | v1.0.0 | `55514ea5c7` | 72 | **C** | CL06 (1), CL16 (4), CL07 (2) |
| `CommitmentLedger` | v2.0.0 | `4490cddec1` | 64 | **D** | CL06 (1), CL16 (4), CL07 (2), CL12 (1) |
| `CommitmentLedger` | v2.1.0 | `4fbef50953` | 64 | **D** | CL06 (1), CL16 (4), CL07 (2), CL12 (1) |
| `CommitmentLedger` | v2.2.0 | `2b73b02c99` | 64 | **D** | CL06 (1), CL16 (4), CL07 (2), CL12 (1) |
| `CommitmentLedger` | v3.0.0 | `0aeab14563` | 74 | **C** | CL06 (3), CL16 (5), CL12 (1) |
| `CommitmentLedger` | v3.1.0 | `616d92d6ab` | 74 | **C** | CL06 (3), CL16 (5), CL12 (1) |
| `CitationWatch` | v1.0.0 | `db7efa656f` | 59 | **D** | CL16 (5), CL07 (2), CL12 (3) |
| `CitationWatch` | v1.1.0 | `fe0e1b82bf` | 83 | **B** | CL16 (5), CL07 (1) |
| `CitationWatch` | v1.2.0 | `7726ce992f` | 80 | **B** | CL16 (5), CL06 (1), CL12 (1) |
| `GuardArena` | current | `1d05532db5` | 85 | **B** | CL06 (2), CL16 (5) |

## (d) Public GenLayer Examples (Neutral Reference Measurements)

*Note: These are public educational examples from `yeagerai/genlayer-simulator` pinned by commit `c94072951e483510329670aa427fba3fa6944f45`. Findings indicate conventions for this pinned rule catalogue and do not imply defects in production systems.*

| Contract | Source | Score | Grade | Findings Detected |
|---|---|---|---|---|
| `storage.py` | `yeagerai/genlayer-simulator` | 94 | **A** | CL01 (1), CL16 (1) |
| `tip_jar.py` | `yeagerai/genlayer-simulator` | 97 | **A** | CL01 (1) |
| `wizard_of_coin.py` | `yeagerai/genlayer-simulator` | 91 | **A** | CL01 (1), CL16 (1), CL14 (1), CL18 (1) |

## (e) Manual Precision Review

- **Total Non-INFO Findings Sampled**: 35
- **Confirmed True Positives**: 35
- **Overall Empirical Precision**: 100.0%

| Rule | Sampled | Confirmed | Unconfirmed | Precision |
|---|---|---|---|---|
| `CL06` | 7 | 7 | 0 | 100% |
| `CL16` | 17 | 17 | 0 | 100% |
| `CL07` | 8 | 8 | 0 | 100% |
| `CL12` | 3 | 3 | 0 | 100% |

## (f) Bounded Model Layer Judgement Stability

- **Labelled Code Excerpts Evaluated**: 15
- **Stable and Correct Judgements**: 15 / 15 (100.0%)
- **Safety Cap**: Model penalty is strictly capped at 20 points. Unverifiable quotes are downgraded to UNCLEAR (0 points).
