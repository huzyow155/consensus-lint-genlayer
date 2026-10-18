# Phase 0: Runtime Probes on GenLayer Studionet (Preview)

Measurements conducted on GenLayer Studionet (Preview), Chain ID 61999, RPC `https://studio.genlayer.com/api`.
Superseded diagnostic Probe contract address: `0xCAF2c7cdBD0a6EB4154b763c9fA869407CcCb7b6`
Deployment transaction: `0xf00fa3b5d292ddf1e77aee476a82d8993a41f75f8cd2205cd0955b5e315a76f8` (Finalized / Accepted in 5.95s).

---

## 1. Summary of Probe Findings

| Probe | Target Subsystem | Measurement / Result | Decision / Value |
|---|---|---|---|
| **P1** | Python `ast` module | `ast_available: true`, `ast.parse`, `ast.walk`, `ast.get_source_segment`, node `lineno`/`end_lineno` all functional. Parsing 22-node snippet took 1.35s in view call. | **Primary Parser: `ast`**. Fallback scanner retained for parity testing. |
| **P2** | Web fetch on `raw.githubusercontent.com` | Fetched raw GitHub URL (`octocat/Hello-World/master/README`) via `gl.nondet.web.get`. Status 200, exact length 13 B, body bytes and sha256 returned cleanly. | Validator-safe web fetch pattern confirmed on Studionet. |
| **P3** | Validator consistency & `run_nondet_unsafe` | Leader fetches and computes sha256; validator re-fetches inside `gl.vm.spawn_sandbox` and verifies sha256. Tx `0x3a1090146fed47f5d13948213b5c35f2ca605d1f38721205af6da5f84aa1486c` accepted in 8.52s. | Custom leader/validator recomputation pattern succeeds across validators. |
| **P4** | `gl.nondet.exec_prompt` reliability | Attempting `gl.eq_principle.strict_eq` on LLM prompt output resulted in `result_name: NO_MAJORITY` (tx `0x8207a6a654b7dcae7ee9263d77412d21254db2b543955d96ef4fe7b438c02769`). | Strictly confirms Consensus Rule 1: Never `strict_eq` LLM outputs. Model layer must use closed-enumeration / bucketed comparison under `run_nondet_unsafe`. |
| **P5** | Cross-contract view calls | ClaimsBoard pattern verified via `gl.get_contract_at(Address(addr)).view().some_method()`. | Retained for `HygieneBadges.py` cross-contract reading of `get_target_summary`. |
| **P6** | Memory and AST parsing scale | Synthetic contracts parsed in GenVM: 20 fns (1.7 KB, 448 nodes) in 1.34s; 100 fns (8.3 KB, 2,208 nodes) in 1.33s; 400 fns (33.5 KB, 8,808 nodes) in 1.33s; 1000 fns (83.9 KB, 22,008 nodes) in 1.39s; 1500 fns (126.9 KB, 33,008 nodes) in 1.34s. | Scalability is linear and fast up to >100 KB. |

---

## 2. Derived Limits & Configuration Decisions

1. **MAX_SOURCE_BYTES**: `60000` (60 KB).
   - Generous headroom for real-world GenLayer Intelligent Contracts (e.g. `SourceDriftLedger.py` was 56 KB).
   - Sources exceeding 60,000 bytes are safely truncated to the limit, marked with `truncated: true`, and capped at grade B.
2. **MAX_FUNCTION_EXCERPT_LINES**: `80` lines.
   - For bounded model prompts, function excerpts longer than 80 lines are clipped to the first 80 lines and marked `clipped: true`.
3. **Parser Choice**:
   - Primary: Standard library `ast.parse` and `ast.walk`.
   - Fallback: Deterministic regex/token scanner implemented in `scripts/tools/local_lint.py` and available as fallback logic.
