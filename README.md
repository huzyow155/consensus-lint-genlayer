# ConsensusLint

**Validator-Verified Consensus-Hygiene Linter for GenLayer Intelligent Contracts on GenLayer Studionet (Preview)**

ConsensusLint is a decentralized, validator-verified static analysis engine and ledger contract for GenLayer Intelligent Contracts. It inspects pinned Python contract source code against a codified 18-rule consensus-hygiene catalogue, calculates an objective hygiene score and grade, persists revision history on-chain, and composes with a companion badges contract via cross-contract view calls.

> [!IMPORTANT]
> **Scope & Honest Limitations**: ConsensusLint is a static linter over a pinned rule catalogue for one SDK version (`py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`). It is **not** a security audit and cannot prove that an Intelligent Contract is correct, bug-free, or free of risk patterns. Every output carries this statement.

---

## 1. Problem Statement: Why Consensus Fails on GenVM

GenLayer introduces Intelligent Contracts: contracts written in Python that can fetch web data and execute LLM prompts under non-deterministic consensus rules. However, builders repeatedly make the same consensus-hygiene mistakes:
1. **Whole-Payload `strict_eq`**: Using `gl.eq_principle.strict_eq` on model outputs or dynamic JSON payloads produces `NO_MAJORITY` consensus failure because LLMs and serialization order exhibit minor non-deterministic phrasing differences across validators.
2. **Leader Trust Violations**: Validators waving through unverified leader calldata or returning `True` unconditionally.
3. **Unchecked Exceptions in Validators**: Catching errors with `except Exception: return True`, allowing invalid state transitions to be accepted.
4. **`TreeMap` Assignment in `__init__`**: Directly overwriting `self.records = {}` inside `__init__`, bypassing GenVM lazy metadata persistence.
5. **Wall-Clock Time Divergence**: Calling `datetime.now()` or `time.time()` instead of the deterministic chain clock `gl.message_raw["datetime"]`.
6. **Insecure URL Filtering**: Validating source or webhook URLs using `.startswith()` or substring containment without full URL parsing.

Traditional Python linters (flake8, pylint) have no awareness of GenVM runtime semantics, leader-validator roles, or consensus wrappers. ConsensusLint solves this by deploying the rule engine directly to **GenLayer Studionet (Preview)**, where validators fetch the contract source, parse the Abstract Syntax Tree (AST), evaluate consensus hygiene, and vote on closed-enumeration verdicts.

---

## 2. Architecture & How It Works

```mermaid
flowchart TD
    User["Developer / Submitter"] -->|register_target / audit_target| CL["ConsensusLint Ledger Contract\n(contracts/ConsensusLint.py)"]
    CL -->|gl.nondet.web.get| GH["GitHub Raw Source\n(raw.githubusercontent.com)"]
    CL -->|Leader Sandbox| L["Leader AST Parsing & Rule Engine\n(Penalty Score & Closed Verdict)"]
    L -->|Leader Calldata| V["Validator Recomputation Sandboxes\n(run_nondet_unsafe)"]
    GH -->|Validator Re-fetch| V
    V -->|Compare SHA-256 & Rule Counts| VOTE["Validator Consensus Vote\n(e.g. 3/5 Majority Agreement)"]
    VOTE -->|Persist Audit Record| STORE["Ledger Storage\n(targets, audits, longitudinal progress)"]
    STORE -->|get_target_summary| HB["HygieneBadges Contract\n(contracts/HygieneBadges.py)"]
    HB -->|Issue / Refresh| BADGE["Target Badges (BADGE_A to BADGE_F)"]
```

### Consensus-Safe Mechanics
- **Independent Validator Recomputation**: Validators never trust the leader's findings or line quotes. Every validator independently re-fetches the source inside `gl.vm.spawn_sandbox`, checks the source SHA-256, and re-executes the AST engine.
- **Closed-Enumeration Verdicts**: Consensus is reached over `source_sha256`, target `mode` (`CONTRACT` vs `NOT_A_CONTRACT`), rule violation counts, and a discrete penalty bucket (`penalty // 5 * 5`). Free-text findings are committed only after the closed-enumeration verdict is accepted by validators.
- **Bounded Model Layer**: LLM prompts are limited to at most 3 call sites, clipped to 80 lines each, and require verbatim quote verification in GenVM code before any penalty is applied.

---

## 3. Deployed Contract Addresses

Deployed and active on **GenLayer Studionet (Preview)** (Chain ID `61999`, RPC `https://studio.genlayer.com/api`):

| Contract | Address | Status | Source SHA-256 |
|---|---|---|---|
| **ConsensusLint** | `0xE2cBaf1916Df7C742486B2eC4E5d3A3289115F2D` | Active | `04337cfc91fe45f76042dba860adf4d9f1567e68fabb525838fa7dffaf4d313b` |
| **HygieneBadges** | `0x3CA9E1b7804b442eaA932ae190d494D4A59295bF` | Active | `64181bc3a3965e9427039a8dec504f0c25aeb4e7e9186b54ba426aadb5bb48b8` |
| **Probe (superseded diagnostic)** | `0xCAF2c7cdBD0a6EB4154b763c9fA869407CcCb7b6` | Superseded Diagnostic | `35de2f50206bac0addafb711623795519d8f67efd631e0388b49e9b8c425989b` |

---

## 4. Rule Catalogue (CL01 - CL18)

| Rule ID | Severity | Method | Description |
|---|---|---|---|
| `CL01` | MINOR (3 pts) | STRUCTURAL | Missing or invalid version header (`# v0.2.<n>`). |
| `CL02` | MAJOR (8 pts) | STRUCTURAL | Missing or invalid `py-genlayer` dependency pin. |
| `CL03` | MINOR (3 pts) | STRUCTURAL | Non-ASCII characters present in contract source. |
| `CL04` | INFO (0 pts) | STRUCTURAL | File does not define a class deriving from `gl.Contract` (Grade F). |
| `CL05` | MAJOR (8 pts) | STRUCTURAL | Assignment into `TreeMap` attribute inside `__init__`. |
| `CL06` | MINOR (3 pts) | HEURISTIC | Unbounded list load-append-store pattern in public write method. |
| `CL07` | MAJOR (8 pts) | HEURISTIC | `strict_eq` called on dynamic payload or free-text. |
| `CL08` | MAJOR (8 pts) | STRUCTURAL | Non-deterministic call (`gl.nondet.*`) outside consensus wrapper. |
| `CL09` | CRITICAL (20 pts) | STRUCTURAL | Validator does not recompute verdict or unconditionally returns `True`. |
| `CL10` | MAJOR (8 pts) | STRUCTURAL | Validator accesses leader calldata without `gl.vm.Return` verification. |
| `CL11` | MAJOR (8 pts) | STRUCTURAL | Validator waves through failures in `except` handler (`return True`). |
| `CL12` | MAJOR (8 pts) | HEURISTIC | Silent default fallback on model parse failure inside `try-except`. |
| `CL13` | MAJOR (8 pts) | STRUCTURAL | Wall-clock time call used (`datetime.now()`) instead of chain clock. |
| `CL14` | MINOR (3 pts) | STRUCTURAL | Generic `raise Exception` or `assert` used instead of `gl.vm.UserError`. |
| `CL15` | MAJOR (8 pts) | HEURISTIC | URL validation by substring or prefix check without `urllib.parse`. |
| `CL16` | MINOR (3 pts) | HEURISTIC | Unbounded string parameter in public write method without `len()` check. |
| `CL17` | MINOR (3 pts) | HEURISTIC | Unpaginated view method iterating state collection without `limit`. |
| `CL18` | INFO (0 pts) | HEURISTIC | Public parameter inserted into prompt template without sanitization. |

See [`docs/RULES.md`](docs/RULES.md) for full rationale, bad snippets, and good snippets.

---

## 5. Scoring & Grades

The hygiene score begins at 100 and applies deducted weights per rule with per-rule severity caps:
- **Grade A**: 90 - 100 (High consensus hygiene)
- **Grade B**: 80 - 89 (Good hygiene; minor items or truncation cap)
- **Grade C**: 70 - 79 (Moderate hygiene; multiple minor or major findings)
- **Grade D**: 60 - 69 (Fair hygiene; contains anti-patterns)
- **Grade F**: 0 - 59 (Failed structural requirements or `NOT_A_CONTRACT`)

Dogfooding result: Both `ConsensusLint.py` and `HygieneBadges.py` score **Grade A (94)** under their own rules.

---

## 6. Quickstart & How to Run

### Requirements
- Node.js v18+ with `genlayer-js`
- Python 3.10+
- Access to GenLayer Studionet (Preview)

### Run Unit & Consensus Tests
```bash
python -m unittest discover tests
```

### Run Safety Scans
```bash
python scripts/tools/scan_ascii.py
python scripts/tools/scan_banned_words.py
```

### Run Empirical Calibration
```bash
python scripts/tools/calibrate.py
```

### Verify Deployment & Evidence Consistency
```bash
node scripts/tools/check_evidence_consistency.js
node scripts/tools/render_evidence.js
```

---

## 7. Documentation Index

- [`docs/DESIGN.md`](docs/DESIGN.md): System architecture, AST vs fallback scanner, consensus-safety principles, threat model.
- [`docs/RULES.md`](docs/RULES.md): Complete catalogue of CL01-CL18 with examples.
- [`docs/PROBES.md`](docs/PROBES.md): Phase 0 runtime probe measurements on Studionet.
- [`docs/CALIBRATION.md`](docs/CALIBRATION.md): Fixture precision/recall, historical timeline, manual review, model calibration.
- [`docs/EVIDENCE.md`](docs/EVIDENCE.md): Complete on-chain evidence with full transaction hashes and validator agreements.
