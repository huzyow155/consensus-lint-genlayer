# On-Chain Evidence & Verification

<!-- onchain:evidence_overview -->
All transactions and audits documented below were executed on **GenLayer Studionet (Preview)** (Chain ID `61999`, RPC `https://studio.genlayer.com/api`, Explorer `https://explorer-studio.genlayer.com`).

> [!NOTE]
> Consensus outcomes are reported as **accepted by validators** with the real consensus agreement ratio (e.g. `3/5`) extracted directly from receipt validator votes. Revert outcomes record the exact decoded `gl.vm.UserError` string returned from GenVM execution with raw base64 leader bytes.

---

## 1. Primary Contract Deployments

<!-- onchain:primary_deployments -->
| Contract | Address | Deploy Transaction Hash | Agreement | Status | Source SHA-256 |
|---|---|---|---|---|---|
| **ConsensusLint** | `0xE2cBaf1916Df7C742486B2eC4E5d3A3289115F2D` | [`0x0f93a3a8679b5ed4e3e7c7acbf848b219834481a91a636e2006d0e3955c1faed`](https://explorer-studio.genlayer.com/tx/0x0f93a3a8679b5ed4e3e7c7acbf848b219834481a91a636e2006d0e3955c1faed) | `3/5` | `ACCEPTED` | `04337cfc91fe45f76042dba860adf4d9f1567e68fabb525838fa7dffaf4d313b` |
| **HygieneBadges** | `0x3CA9E1b7804b442eaA932ae190d494D4A59295bF` | [`0xeef694c69810f8b4f0c16667bffc0b5784d4302617e2136fd7fadf993fd6c609`](https://explorer-studio.genlayer.com/tx/0xeef694c69810f8b4f0c16667bffc0b5784d4302617e2136fd7fadf993fd6c609) | `3/5` | `ACCEPTED` | `64181bc3a3965e9427039a8dec504f0c25aeb4e7e9186b54ba426aadb5bb48b8` |
| **Probe (superseded diagnostic)** | `0xCAF2c7cdBD0a6EB4154b763c9fA869407CcCb7b6` | [`0xf00fa3b5d292ddf1e77aee476a82d8993a41f75f8cd2205cd0955b5e315a76f8`](https://explorer-studio.genlayer.com/tx/0xf00fa3b5d292ddf1e77aee476a82d8993a41f75f8cd2205cd0955b5e315a76f8) | `3/5` | `superseded diagnostic probe` | `35de2f50206bac0addafb711623795519d8f67efd631e0388b49e9b8c425989b` |

### Inter-Contract Configuration
<!-- onchain:set_ledger -->
- **`HygieneBadges.set_ledger` Tx**: [`0x7c5de5bd4d971573b2d555a0b6bb31b6fbfdad93e82c78521f495a52f249e328`](https://explorer-studio.genlayer.com/tx/0x7c5de5bd4d971573b2d555a0b6bb31b6fbfdad93e82c78521f495a52f249e328)
- **Agreement**: `3/5`
- **Configured Ledger**: `0xe2cbaf1916df7c742486b2ec4e5d3a3289115f2d`
- **Deployer / Owner**: `0xe2d9062adc5f4b6061788996f859b224a7a8745c`

---

## 2. On-Chain Positive Fixture Audits

<!-- onchain:fixture_audits -->
| Fixture Target | Target ID | Register Tx | Audit Tx | Agreement | Score | Grade | Truncated | Findings Count |
|---|---|---|---|---|---|---|---|---|
| **GoodContract Fixture** | `2bac0b36b071` | [`0xe34599052b01...`](https://explorer-studio.genlayer.com/tx/0xe34599052b017303aa4f76166cfe6d73a52b3c860db0fc5d28e87f235f01ffc0) | [`0xac076107559e...`](https://explorer-studio.genlayer.com/tx/0xac076107559e4f790a81124e95502ce80f90fa5930255f98bfcd4bd02efe6208) | `3/5` | **94** | **A** | `false` | 0 rules |
| **BadContract Fixture** | `9bd135be77a6` | [`0x70cf2f5a9c3a...`](https://explorer-studio.genlayer.com/tx/0x70cf2f5a9c3a89143c0735f1281a338e2a7b787032044c0532a0009f8e4f6d65) | [`0xdff2cc66ff68...`](https://explorer-studio.genlayer.com/tx/0xdff2cc66ff68a5f1fcef2b0822bed2555ef952d69e78198a93c02da2450bb119) | `3/5` | **0** | **F** | `false` | 17 rules |
| **MixedContract Fixture** | `c3e533a5f89e` | [`0x97e4e3646f17...`](https://explorer-studio.genlayer.com/tx/0x97e4e3646f171dbfa046ef7004822e80f40c1f894e80510b8527298209a78126) | [`0x05918df9e749...`](https://explorer-studio.genlayer.com/tx/0x05918df9e749015476439244b09b5994801b9f1d24793e97442d6c162b9afb62) | `3/5` | **86** | **B** | `false` | 3 rules |
| **NotAContract Fixture** | `fc8f14409f6b` | [`0x65fecc13dc07...`](https://explorer-studio.genlayer.com/tx/0x65fecc13dc07ed362654e7e28d845e8b21af6e7b4e8eac027526efb5c597b445) | [`0xb2cd69f4f5bb...`](https://explorer-studio.genlayer.com/tx/0xb2cd69f4f5bb7f47bcb83177e84c6571339777b8f395aeb6087e084bee2cb3cf) | `3/5` | **-1** | **N/A** | `false` | 0 rules |
| **ShellLike Large Fixture (partial/truncated audit)** | `dca608d38708` | [`0xffcf75e987dd...`](https://explorer-studio.genlayer.com/tx/0xffcf75e987ddfc8dbd0faf9d38661c79b5c55ad519658f041a8850c3443c9bc2) | [`0xd52ffe6ba839...`](https://explorer-studio.genlayer.com/tx/0xd52ffe6ba839557d5e1db354325e63ce34631bc9c5b1e373285c753035d7d9e9) | `3/5` | **100** | **B** | `true` | 0 rules |
| **EvolvingContract Fixture** | `2a4fabcda5ed` | [`0xb1e511e54bcb...`](https://explorer-studio.genlayer.com/tx/0xb1e511e54bcbf48424f64e8f367009e08b5727a74435f3e18349ab16d4f337dc) | [`0x681b94d2474c...`](https://explorer-studio.genlayer.com/tx/0x681b94d2474c2f469c5a71824746a97f837fcada101d5efc080f95f571a11996) | `3/5` | **83** | **B** | `false` | 3 rules |

> [!WARNING]
> **ShellLike Large Fixture Truncation Note**: ShellLike (196,016 bytes) exceeded `MAX_SOURCE_BYTES` (60,000 bytes). It was linted only on its first complete lines within 60,000 bytes (~30% of file bytes). While its score is 100 in that partial segment, its grade is capped at **Grade B** on-chain.

---

## 3. On-Chain Dogfooding (Self-Lint)

<!-- onchain:self_lint -->
ConsensusLint evaluated its own deployed contracts directly via validator re-fetch from GitHub. Note that `ConsensusLint.py` (66,505 bytes) exceeded `MAX_SOURCE_BYTES` (60,000 bytes), so it was linted up to byte 60,000; its unlinted tail (lines 1287-1438, 6,505 bytes) was verified locally via `scripts/tools/lint_tail.py` (LOCAL run: 100/100, Grade A, 0 findings).

| Contract | Target ID | Register Tx | Audit Tx | Agreement | Hygiene Score | Grade | Key Rule Findings |
|---|---|---|---|---|---|---|---|
| **ConsensusLint Ledger Contract (partial/truncated self-lint)** | `09534c63a674` | [`0xcf663b5cc28a...`](https://explorer-studio.genlayer.com/tx/0xcf663b5cc28a03677639688a4a7f3561cf3ae85651b95e952f70bf6f1dee602a) | [`0x79486100dde3...`](https://explorer-studio.genlayer.com/tx/0x79486100dde3d3a0bb81b3c89725f2e43833e2b70e90902929d460bdb1cedfd5) | `3/5` | **90** | **B** | `CL06, CL16` |
| **HygieneBadges Contract** | `810898e24e1d` | [`0x6238bdfb7323...`](https://explorer-studio.genlayer.com/tx/0x6238bdfb73237c1c228cc867d0e47eba09e075b71fcdc4bfe3dcdff66435f713) | [`0x5d0c1b8335f8...`](https://explorer-studio.genlayer.com/tx/0x5d0c1b8335f827acea81e9822835d149465f120baeb0ef281712fa261f55298c) | `3/5` | **94** | **A** | `CL06, CL16` |

### Model Layer Judgements (J1 - J3) on Active Contracts
<!-- onchain:model_judgements -->
| Contract / Target | Question | Judgement Label | Quote Verified | Penalty | Verbatim Code Quote |
|---|---|---|---|---|---|
| GoodContract Fixture (`2bac0b36b071`) | `J1` | `RECOMPUTES` | `true` | -6 pts | `val_sand = gl.vm.spawn_sandbox(val_fetch)             if not isinstance(val_sand, gl.vm.Return):                 return False             return val_sand.calldata == ldata.get("sha256")` |
| GoodContract Fixture (`2bac0b36b071`) | `J2` | `FREE_TEXT_OR_PAYLOAD` | `true` | -6 pts | `return val_sand.calldata == ldata.get("sha256")` |

---

## 4. Maintainer Finding Response Flow

<!-- onchain:maintainer_responses -->
Contract registrants can attach documented responses with a structured stance (`FIXED_NEXT`, `DISPUTE`, `WONTFIX`) to specific findings without altering consensus verdicts:

- **Target ID**: `9bd135be77a6` (Audit #1)
- **Rule**: `CL05`
- **Stance**: `FIXED_NEXT`
- **Response Note**: *"Acknowledged: TreeMap lazy initialization will be adopted in next patch."*
- **Transaction Hash**: [`0xef692ee4b317a14dd7f55e834dc10daae13f185edde629c08a24b1a12580d562`](https://explorer-studio.genlayer.com/tx/0xef692ee4b317a14dd7f55e834dc10daae13f185edde629c08a24b1a12580d562) (Agreement `3/5`, Elapsed `9.67s`)
- **Stored Responses Array**: `[{"at":"2026-10-19T06:52:06Z","by":"0xe2d9062adc5f4b6061788996f859b224a7a8745c","note":"Acknowledged: TreeMap lazy initialization will be adopted in next patch.","rule_id":"CL05","stance":"FIXED_NEXT"}]`


---

## 5. HygieneBadges On-Chain Verification

<!-- onchain:badges -->
Cross-contract view composition via `gl.get_contract_at(Address(ledger_address)).view().get_target_summary(target_id)`:

| Badge ID | Target ID | Display Name | Current Status | Grade | Score | Claim Tx Hash | Agreement |
|---|---|---|---|---|---|---|---|
| `530360cf70b6` | `2bac0b36b071` | GoodContract Official Badge | `BADGE_A` | **A** | 94 | [`0x57a58324c86f...`](https://explorer-studio.genlayer.com/tx/0x57a58324c86f1e0d951d66d82a0045ca584b951b1ed26a8d64ee812794588a03) | `3/5` |
| `a3ac759ddcec` | `09534c63a674` | ConsensusLint Core Badge | `BADGE_B` | **B** | 90 | [`0x4d40c3c8e661...`](https://explorer-studio.genlayer.com/tx/0x4d40c3c8e661a16b62e3a9a57e1ddeef9c317d16283c979338a1488b459a9766) | `4/5` |
| `9e019f3c3320` | `2a4fabcda5ed` | EvolvingContract Badge | `BADGE_A` | **A** | 100 | [`0x5fdfc763c985...`](https://explorer-studio.genlayer.com/tx/0x5fdfc763c98567dd41bd26dfa2b65ada08b809446b8339c717be987fecd84fa3) | `3/5` |

> [!NOTE]
> **Badge Minting on Truncated Audits**: HygieneBadges verifies the target summary score and grade from ConsensusLint, but does not refuse badges when `truncated == true`. The BADGE_B for ConsensusLint was issued on its truncated audit (Score 94, Grade B).

---

## 6. Decoded Negative Revert Tests

<!-- onchain:negative_tests -->
Every negative constraint is rejected deterministically via `raise gl.vm.UserError("<exact message>")`. Receipts record execution status `ERROR` with the decoded error string verified against contract literals, alongside raw base64 leader bytes:

| Test ID | Description | Transaction Hash | Receipt Status | Agreement | Raw Base64 Leader Bytes | Decoded `gl.vm.UserError` | Result |
|---|---|---|---|---|---|---|---|
| **NEG-01** | Reject URL with unauthorized host | [`0xb1d53c7634f3...`](https://explorer-studio.genlayer.com/tx/0xb1d53c7634f3e7be8eb6460b546defae34f6879dd7074fccd22ac3c52fde9d25) | `ACCEPTED` | `3/5` | `AXNvdXJjZSBob3N0IG5vdCBhbGxvd2Vk` | `"source host not allowed"` | **PASS** |
| **NEG-02** | Reject duplicate target registration by same sender | [`0x5ca4ed2438bf...`](https://explorer-studio.genlayer.com/tx/0x5ca4ed2438bf2ba112290f0a181e4b671c3c6c8db5943e2c12c45c783969529a) | `ACCEPTED` | `3/5` | `AXRhcmdldCBhbHJlYWR5IHJlZ2lzdGVyZWQ=` | `"target already registered"` | **PASS** |
| **NEG-03** | Enforce 300-second audit cooldown on rapid re-audit | [`0x629c753f7d87...`](https://explorer-studio.genlayer.com/tx/0x629c753f7d87c55a6b3c1405b56146b0a1118249bcf6c8dd984c6363ff39c6d5) | `ACCEPTED` | `3/5` | `AWF1ZGl0IGNvb2xkb3duIGFjdGl2ZQ==` | `"audit cooldown active"` | **PASS** |
| **NEG-04** | Reject finding response from non-registrant sender | [`0x97b9c8dc7280...`](https://explorer-studio.genlayer.com/tx/0x97b9c8dc7280c15ba8c5c36129cdf2ca268e54c28dd038e5f20f7e42581835fa) | `ACCEPTED` | `3/5` | `AW9ubHkgdGhlIHJlZ2lzdHJhbnQgY2FuIGRvIHRoaXM=` | `"only the registrant can do this"` | **PASS** |
| **NEG-05** | Reject badge claim for non-existent target ID | [`0x31d770988193...`](https://explorer-studio.genlayer.com/tx/0x31d77098819383c968b5f16c2a543c16e710c2edd640bb0d3ae5ab2ffa825c14) | `ACCEPTED` | `3/5` | `AXRhcmdldCBub3QgZm91bmQgaW4gbGVkZ2Vy` | `"target not found in ledger"` | **PASS** |
| **NEG-06** | Reject finding response with invalid stance | [`0x388dadf96d62...`](https://explorer-studio.genlayer.com/tx/0x388dadf96d62f9989fde9bcdb46085e02416f3adbf622382f4550488c6bd7ef6) | `ACCEPTED` | `3/5` | `AWludmFsaWQgc3RhbmNl` | `"invalid stance"` | **PASS** |
| **NEG-07** | Reject finding response for rule not present in audit | [`0x54e2fba8652f...`](https://explorer-studio.genlayer.com/tx/0x54e2fba8652f824915b9edfa08f2c26b14e96fe0d0deff004e3d421195c2bd59) | `ACCEPTED` | `3/5` | `AWZpbmRpbmcgbm90IHByZXNlbnQgaW4gYXVkaXQ=` | `"finding not present in audit"` | **PASS** |

---

## 7. Real-World Historical Contract Audits On-Chain

<!-- onchain:historical_targets -->
Four historical Intelligent Contract versions were registered and audited on **GenLayer Studionet (Preview)** through ConsensusLint:

| Contract Target | Target ID | Register Tx | Audit Tx | Agreement | On-Chain Score | On-Chain Grade | Expected Local Score | Delta vs Local |
|---|---|---|---|---|---|---|---|---|
| **CitationWatch v1.0.0** | `ceac13c5c45b` | [`0xcb29936238e4...`](https://explorer-studio.genlayer.com/tx/0xcb29936238e4a046882395c579a924163a74e079fe13f61000a684c60530ac43) | [`0xd8c25b23605e...`](https://explorer-studio.genlayer.com/tx/0xd8c25b23605ecad62123691f58ed673e3fbb92285f8a84aa9cade2a73087565e) | `3/5` | **52** | **D** | 59 (D) | -7 |
| **CitationWatch v1.1.0** | `4f5fe08eced6` | [`0xf320bf3a8850...`](https://explorer-studio.genlayer.com/tx/0xf320bf3a8850bc95d8435e0f8bc0f468578bd036d97cd60951ce09d241640943) | [`0xa291cfde947b...`](https://explorer-studio.genlayer.com/tx/0xa291cfde947bb2f9ad7db0a2253eba0a275143516b09142bddc1edebfce97292) | `3/5` | **80** | **B** | 83 (B) | -3 |
| **CitationWatch v1.2.0** | `e4870f0eb5dc` | [`0x0a9325a7bdb8...`](https://explorer-studio.genlayer.com/tx/0x0a9325a7bdb8b69445a6aac6164b88db22849c8c1580e0a6754356a47c55f748) | [`0xe71a2a29fadf...`](https://explorer-studio.genlayer.com/tx/0xe71a2a29fadf7e7fb2dea80285a68e2b6c2dc81fadcea7f3d72cc73a2bda97cd) | `3/5` | **78** | **C** | 80 (B) | -2 |
| **CommitmentLedger v3.1.0** | `f3c98282cef3` | [`0xff79469d1b7d...`](https://explorer-studio.genlayer.com/tx/0xff79469d1b7d5020278e89941767c11803dd97c4672a7c994b49aeda28a7df72) | [`0x4c61ba019948...`](https://explorer-studio.genlayer.com/tx/0x4c61ba0199488edad7b384471e488e0447a4d6d303177bf6252c0c18e68ea0ab) | `3/5` | **74** | **C** | 74 (C) | +0 |

---

## 8. Observed On-Chain Validator Disagreement

<!-- onchain:disagreed_runs -->
In accordance with Standing Rule 0 ("Every failed/disagreed/timed-out/reverted tx is recorded in the evidence JSON"), this transaction records real-world validator disagreement observed on Studionet:

| Target | Transaction Hash | Status | Result Name | Round Votes | Agreement | Explanation |
|---|---|---|---|---|---|---|
| CitationWatch v1.2.0 (attempt 1) | [`0x93bcc19aa511...`](https://explorer-studio.genlayer.com/tx/0x93bcc19aa51136ff997ccdc2a459f357be8e0441bff45185af2bb0850032e06b) | `FINALIZED` | `MAJORITY_DISAGREE` | `AGREE, DISAGREE, DISAGREE, AGREE, DISAGREE` | 2/5 | Observed on-chain consensus disagreement: 3 validators voted DISAGREE in round 3, leading to status UNDETERMINED (MAJORITY_DISAGREE). Real agreement 2/5. |

---

## 9. Superseded Runs & Diagnostics

<!-- onchain:superseded_runs -->
| Type | Transaction Hash | Reason / Root Cause |
|---|---|---|
| `maintainer_response` | [`0x597108fa1eb8...`](https://explorer-studio.genlayer.com/tx/0x597108fa1eb8ac3c314a8fd2de20dbc80391b9fc74a176d37cf834016a2768f3) | Called with 4 arguments; leader execution ERROR; nothing stored |
| `maintainer_response` | [`0xc5e3fd89148e...`](https://explorer-studio.genlayer.com/tx/0xc5e3fd89148e8256c8226f0fc36e044523daec03dd7399fcafcc6c6d5f1aed2d) | Called with 4 arguments; leader execution ERROR; nothing stored |

---

## 10. Evolving Contract & Longitudinal Progress Verification

<!-- onchain:evolving_progress -->
| Metric | Older Audit (#1) | Newer Audit (#2) | Delta |
|---|---|---|---|
| **Source SHA-256** | `0efc8681b2c54976...` | `8d06354a18174181...` | Modified |
| **Hygiene Score** | **83** | **100** | **+17 points** |
| **Grade** | **B** | **A** | **Improved** |

### Per-Rule Finding Deltas
- **Rule `CL15`**: Before = 1, After = 0 (Delta: `-1`)
- **Rule `CL16`**: Before = 2, After = 0 (Delta: `-2`)
- **Rule `CL17`**: Before = 1, After = 0 (Delta: `-1`)

---

## 11. Fixture & Sample Statistics (n=7 targets, 5 synthetic)

<!-- onchain:ecosystem_views -->
- **Total Targets Registered**: `8`
- **Total Audits Performed**: `10`
- **Scored Targets**: `7`

### Leaderboard Top Targets
- **ShellLike Large Fixture** (`dca608d38708`): Score 100 (Grade B)
- **EvolvingContract Fixture** (`2a4fabcda5ed`): Score 100 (Grade A)
- **GoodContract Fixture** (`2bac0b36b071`): Score 94 (Grade A)
- **HygieneBadges Contract** (`810898e24e1d`): Score 94 (Grade A)
- **ConsensusLint Ledger Contract** (`09534c63a674`): Score 90 (Grade B)
- **MixedContract Fixture** (`c3e533a5f89e`): Score 86 (Grade B)
- **BadContract Fixture** (`9bd135be77a6`): Score 0 (Grade F)

> [!NOTE]
> **Leaderboard Note on Truncation**: ShellLike is a truncated audit; the board ranks by score and does not exclude truncated audits.

---

## 12. Verification & Traceability Summary

### Observed on-chain on the active deployment:
- Contract deployments (ConsensusLint, HygieneBadges, set_ledger)
- Positive fixture audits (GoodContract, BadContract, MixedContract, NotAContract, ShellLike)
- Self-lint dogfooding (ConsensusLint and HygieneBadges)
- Longitudinal progress (EvolvingContract v1 to v2, get_progress)
- Maintainer response flow (respond_to_finding with stance, stored responses array verified)
- HygieneBadges issuance & query (claim_badge, get_badge)
- Decoded negative reverts (NEG-01 to NEG-07, UserError literals and raw base64 leader bytes)
- Historical real-world audits on-chain (CitationWatch v1.0.0, v1.1.0, v1.2.0, CommitmentLedger v3.1.0)
- Observed validator disagreement (CitationWatch v1.2.0 attempt 1: UNDETERMINED, MAJORITY_DISAGREE, 2/5)
- Public ledger aggregations (get_board, get_rule_stats, list_target_ids, list_series)

### Unit-tested only (until proven on-chain):
- Response count limit (MAX_RESPONSES_PER_AUDIT = 10 rejection)
- Model layer prompt injection resilience and fallback downgrade
- Disagreement paths in fallback regex scanner
- Pagination bounds > 50 rejection
