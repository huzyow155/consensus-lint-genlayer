# ConsensusLint Architecture & Design Specification

**ConsensusLint** is a validator-verified consensus-hygiene linter designed specifically for GenLayer Intelligent Contracts running on **GenLayer Studionet (Preview)**.

> [!IMPORTANT]
> **Scope & Honest Limitations**: ConsensusLint is a static linter over a pinned rule catalogue for one SDK version. It is not a security audit and cannot prove that an Intelligent Contract is correct or free of risk patterns. ConsensusLint identifies known anti-patterns, non-deterministic traps, and consensus-hygiene violations.

---

## 1. System Motivation

GenLayer Intelligent Contracts differ fundamentally from traditional smart contracts:
1. **Execution Environment**: GenVM executes Python 3 code directly rather than low-level virtual machine opcodes.
2. **Validator Consensus**: Validators re-execute non-deterministic operations (such as web fetches and model prompts) and reach agreement through leader-validator verification principles.
3. **Common Pitfalls**: Builders frequently encounter recurring consensus anti-patterns:
   - Using whole-payload `strict_eq` across variable model outputs or unpinned JSON keys, leading to consensus failure (`NO_MAJORITY`).
   - Trusting leader calldata without independent recomputation.
   - Waving through exceptions inside validator `except` clauses.
   - Assigning `TreeMap` instances directly in `__init__`, bypassing lazy metadata initialization.
   - Relying on wall-clock time (`datetime.now()`) instead of the deterministic chain clock (`gl.message_raw["datetime"]`).
   - Using substring or prefix checks on untrusted URLs instead of full URL parsing.

ConsensusLint allows developers to register a pinned source URL and have validators independently fetch the source, parse its Abstract Syntax Tree (AST), evaluate 18 consensus rules, and record a verifiable hygiene score and grade on-chain.

```
       +-------------------------------------------------------------+
       |                     Developer / User                        |
       +-------------------------------------------------------------+
              |                                            ^
     register_target() / audit_target()                    | get_board(), get_target()
              v                                            |
+---------------------------------------------------------------------------------+
|                       ConsensusLint Ledger Contract                             |
|                                                                                 |
|  +--------------------+   gl.nondet.web.get   +------------------------------+  |
|  | Leader Sandbox     | --------------------> | GitHub Raw Source Repository |  |
|  | - AST Parsing      |                       +------------------------------+  |
|  | - Rule Evaluation  |                                      ^                  |
|  | - Score Bucketing  |                                      | re-fetch         |
|  +--------------------+                                      |                  |
|            |                                                 |                  |
|            v leader calldata                                 |                  |
|  +--------------------+                       +------------------------------+  |
|  | Validator Sandboxes| --------------------> | Validator Recomputation      |  |
|  | (run_nondet_unsafe)|                       | - Re-fetch & check SHA-256   |  |
|  |                    |                       | - Re-parse AST & rule counts |  |
|  +--------------------+                       +------------------------------+  |
|            |                                                                    |
|            +--------------------> Ledger State Storage                          |
|                                   - targets[tid], audits[tid:n]                 |
|                                   - Longitudinal Progress & Ecosystem Stats     |
+---------------------------------------------------------------------------------+
                                      ^
                                      | Cross-contract view call
                                      | (get_target_summary)
+-------------------------------------+-------------------------------------------+
|                          HygieneBadges Contract                                 |
|  - Tracks Target Badges (BADGE_A, BADGE_B, BADGE_C, BADGE_D, BADGE_F)           |
|  - Deterministic state machine: Upgrades or Downgrades on newer audits          |
+---------------------------------------------------------------------------------+
```

---

## 2. Core Consensus Design Choices

### 2.1 AST vs Fallback Scanner (Probe P1 & P6)
During Phase 0 runtime probes on GenLayer Studionet (Preview), the Python standard library `ast` module was evaluated on-chain inside GenVM.
- **Probe Result**: `ast.parse` and `ast.walk` parsed up to 126 KB (33,008 nodes) in 1.34s without runtime memory faults.
- **Decision**: Standard `ast` is selected as the primary parser for accuracy. A deterministic fallback line scanner was also created and validated locally.

### 2.2 Recomputation Over Calldata Trust (Rule CL09 & CL10)
In ConsensusLint, validators never blindly trust the leader's findings, counts, or quoted line numbers.
1. The leader fetches source, calculates SHA-256, parses AST, runs the rules, and computes a penalty bucket.
2. The validator independently re-fetches the source in `gl.vm.spawn_sandbox(val_fetch_call)`.
3. The validator verifies the SHA-256 hash matches the leader's claimed hash.
4. The validator re-runs `_LinterEngine(norm_text).run()` and independently computes the rule counts and penalty bucket.
5. If any step mismatches, the validator rejects the leader payload.

### 2.3 Closed-Enumeration Comparison vs Free-Text (Rule CL07 & Probe P4)
Probe P4 proved on-chain that calling `gl.eq_principle.strict_eq` on model outputs produces `NO_MAJORITY` consensus failure due to slight phrasing variations.
To avoid consensus breakdown:
- ConsensusLint compares only closed enumeration values: `source_sha256`, `mode` (`CONTRACT` vs `NOT_A_CONTRACT`), exact integer counts per rule, and a bucketed penalty score (`penalty_bucket = total_penalty // 5 * 5`).
- The detailed findings object is committed to storage only after the closed-enumeration verdict is accepted by validators.

### 2.4 Model Layer Bounding & Verbatim Quote Verification
For judgement questions (e.g. verifying whether a prompt includes unvalidated public parameters):
- The model prompt is strictly bounded (maximum 3 call sites, each excerpt clipped to 80 lines).
- The model must answer with a strict JSON format: `{"site_id": int, "verdict": "VERIFIED_SANITIZED" | "UNSANITIZED_RISK", "quote": str}`.
- GenVM code checks that the returned `quote` exists verbatim in the excerpt. If the quote is missing or hallucinated, the model judgement is discarded without falling back to a silent default.

---

## 3. Limits & Complexity Boundaries

| Parameter | Value | Justification |
|---|---|---|
| `MAX_SOURCE_BYTES` | 60,000 bytes (60 KB) | Probed on Studionet; accommodates production contracts. Sources > 60 KB are truncated to limit and capped at grade B. |
| `MAX_FUNCTION_EXCERPT_LINES` | 80 lines | Prevents model prompt token overflows. |
| `AUDIT_COOLDOWN_SECONDS` | 300 seconds (5 min) | Prevents denial-of-service spam on validator web-fetch bandwidth. |
| `MAX_AUDITS_PER_TARGET` | 10 audits | Bounded storage growth per registered target. |
| `PAGE_LIMIT_MAX` | 50 items | All public views strictly enforce pagination limits. |

### Source Truncation Mechanics & Deployed Behaviour
In `contracts/ConsensusLint.py`, when a contract's source size exceeds `MAX_SOURCE_BYTES` (60,000 bytes):
1. The text is clipped to the last complete line within the first 60,000 bytes via `_clip_to_complete_lines(raw_source, MAX_SOURCE_BYTES)`.
2. The recorded `source_sha256` is the SHA-256 digest of the *truncated* text, not the complete original file.
3. Scoring and grade capping logic in `_compute_score_and_penalty` (lines 871-874):
```python
if score >= 90: grade = "A"
elif score >= 80: grade = "B"
...
if truncated and grade == "A":
    grade = "B"
```
Notice that:
- The **grade** is capped at **Grade B** (cannot earn Grade A).
- The **score** is **NOT** capped; a clean file with 0 findings in its truncated head retains a numerical score of **100**.
- **Leaderboard Impact**: `ConsensusLint.get_board("best")` sorts targets by `(score, last_audit_ts)` without checking `truncated == true`. A truncated file scoring 100 ranks at the top of the board (e.g. `ShellLike Large Fixture`).
- **HygieneBadges Impact**: `HygieneBadges.claim_badge` calls `get_target_summary` to inspect score and grade, but does not check the `truncated` flag, allowing badges to be minted on truncated audits (e.g. `ConsensusLint` self-lint).

---

## 4. Threat Model & Security Mitigations

1. **Malicious Source Injection (`exec`/`eval`/`compile`)**:
   - Threat: A registered URL serves malicious Python code designed to escape GenVM.
   - Mitigation: ConsensusLint treats fetched source strictly as plain text. It never executes, evaluates, imports, or compiles source code.
2. **URL Spoofing & SSRF**:
   - Threat: A submitter provides an internal IP or non-GitHub URL to trigger SSRF in validator nodes.
   - Mitigation: Strict URL parser enforces scheme `https`, host `raw.githubusercontent.com`, port 443, and depth limits. Rejects query parameters, userinfo, IP addresses, and path traversals (`..`).
3. **Validator Desynchronization**:
   - Threat: A mutable git branch (e.g. `main`) changes during multi-validator voting.
   - Mitigation: The leader commits the exact `source_sha256` fetched. Validators fetch independently; if the source hash has changed between validator fetches, consensus falls back safely.
