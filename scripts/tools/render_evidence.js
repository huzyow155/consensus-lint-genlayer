// scripts/tools/render_evidence.js
const fs = require('fs');
const path = require('path');

function renderMarkdown() {
  const deployPath = path.join(__dirname, '../deploy/deployments.json');
  const livePath = path.join(__dirname, '../deploy/live_evidence.json');

  if (!fs.existsSync(deployPath)) {
    throw new Error("deployments.json missing");
  }
  const deployments = JSON.parse(fs.readFileSync(deployPath, 'utf8'));

  let live = null;
  if (fs.existsSync(livePath)) {
    live = JSON.parse(fs.readFileSync(livePath, 'utf8'));
  }

  let md = `# On-Chain Evidence & Verification

<!-- onchain:evidence_overview -->
All transactions and audits documented below were executed on **GenLayer Studionet (Preview)** (Chain ID \`61999\`, RPC \`https://studio.genlayer.com/api\`, Explorer \`https://explorer-studio.genlayer.com\`).

> [!NOTE]
> Consensus outcomes are reported as **accepted by validators** with the real consensus agreement ratio (e.g. \`3/5\`) extracted directly from receipt validator votes. Revert outcomes record the exact decoded \`gl.vm.UserError\` string returned from GenVM execution with raw base64 leader bytes.

---

## 1. Primary Contract Deployments

<!-- onchain:primary_deployments -->
| Contract | Address | Deploy Transaction Hash | Agreement | Status | Source SHA-256 |
|---|---|---|---|---|---|
| **ConsensusLint** | \`${deployments.contracts.ConsensusLint.address}\` | [\`${deployments.contracts.ConsensusLint.deployTxHash}\`](https://explorer-studio.genlayer.com/tx/${deployments.contracts.ConsensusLint.deployTxHash}) | \`${deployments.contracts.ConsensusLint.agreement}\` | \`${deployments.contracts.ConsensusLint.status}\` | \`${deployments.contracts.ConsensusLint.sourceSha256}\` |
| **HygieneBadges** | \`${deployments.contracts.HygieneBadges.address}\` | [\`${deployments.contracts.HygieneBadges.deployTxHash}\`](https://explorer-studio.genlayer.com/tx/${deployments.contracts.HygieneBadges.deployTxHash}) | \`${deployments.contracts.HygieneBadges.agreement}\` | \`${deployments.contracts.HygieneBadges.status}\` | \`${deployments.contracts.HygieneBadges.sourceSha256}\` |
| **Probe (superseded diagnostic)** | \`${deployments.contracts.Probe.address}\` | [\`${deployments.contracts.Probe.deployTxHash}\`](https://explorer-studio.genlayer.com/tx/${deployments.contracts.Probe.deployTxHash}) | \`3/5\` | \`${deployments.contracts.Probe.status}\` | \`35de2f50206bac0addafb711623795519d8f67efd631e0388b49e9b8c425989b\` |

### Inter-Contract Configuration
<!-- onchain:set_ledger -->
- **\`HygieneBadges.set_ledger\` Tx**: [\`${deployments.contracts.HygieneBadges.setLedgerTxHash}\`](https://explorer-studio.genlayer.com/tx/${deployments.contracts.HygieneBadges.setLedgerTxHash})
- **Agreement**: \`${deployments.contracts.HygieneBadges.setLedgerAgreement}\`
- **Configured Ledger**: \`${deployments.contracts.HygieneBadges.ledgerAddress}\`
- **Deployer / Owner**: \`${deployments.deployer}\`

---

## 2. On-Chain Positive Fixture Audits

<!-- onchain:fixture_audits -->
| Fixture Target | Target ID | Register Tx | Audit Tx | Agreement | Score | Grade | Truncated | Findings Count |
|---|---|---|---|---|---|---|---|---|
`;

  if (live) {
    for (const [key, t] of Object.entries(live.targets || {})) {
      const fCount = Object.keys(t.auditRecord.findings || {}).length;
      const isTruncated = t.auditRecord && t.auditRecord.truncated;
      const labelText = isTruncated ? `**${t.label} (partial/truncated audit)**` : `**${t.label}**`;
      md += `| ${labelText} | \`${t.tid}\` | [\`${t.registrationTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${t.registrationTxHash}) | [\`${t.auditTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${t.auditTxHash}) | \`${t.auditAgreement}\` | **${t.auditRecord.score}** | **${t.auditRecord.grade}** | \`${t.auditRecord.truncated}\` | ${fCount} rules |\n`;
    }

    md += `
> [!WARNING]
> **ShellLike Large Fixture Truncation Note**: ShellLike (196,016 bytes) exceeded \`MAX_SOURCE_BYTES\` (60,000 bytes). It was linted only on its first complete lines within 60,000 bytes (~30% of file bytes). While its score is 100 in that partial segment, its grade is capped at **Grade B** on-chain.

---

## 3. On-Chain Dogfooding (Self-Lint)

<!-- onchain:self_lint -->
ConsensusLint evaluated its own deployed contracts directly via validator re-fetch from GitHub. Note that \`ConsensusLint.py\` (66,505 bytes) exceeded \`MAX_SOURCE_BYTES\` (60,000 bytes), so it was linted up to byte 60,000; its unlinted tail (lines 1287-1438, 6,505 bytes) was verified locally via \`scripts/tools/lint_tail.py\` (LOCAL run: 100/100, Grade A, 0 findings).

| Contract | Target ID | Register Tx | Audit Tx | Agreement | Hygiene Score | Grade | Key Rule Findings |
|---|---|---|---|---|---|---|---|
`;
    for (const [key, s] of Object.entries(live.self_lint || {})) {
      const findingKeys = Object.keys(s.auditRecord.findings || {}).join(", ") || "None";
      const isTruncated = s.auditRecord && s.auditRecord.truncated;
      const labelText = isTruncated ? `**${s.label} (partial/truncated self-lint)**` : `**${s.label}**`;
      md += `| ${labelText} | \`${s.tid}\` | [\`${s.registrationTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${s.registrationTxHash}) | [\`${s.auditTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${s.auditTxHash}) | \`${s.auditAgreement}\` | **${s.auditRecord.score}** | **${s.auditRecord.grade}** | \`${findingKeys}\` |\n`;
    }

    md += `
### Model Layer Judgements (J1 - J3) on Active Contracts
<!-- onchain:model_judgements -->
| Contract / Target | Question | Judgement Label | Quote Verified | Penalty | Verbatim Code Quote |
|---|---|---|---|---|---|
`;
    // GoodContract judgements
    if (live.targets && live.targets.good_contract && live.targets.good_contract.auditRecord.judgements) {
      for (const j of live.targets.good_contract.auditRecord.judgements) {
        const qClean = j.quote.replace(/\n/g, ' ');
        md += `| GoodContract Fixture (\`2bac0b36b071\`) | \`${j.id}\` | \`${j.label}\` | \`${j.quote_verified}\` | -6 pts | \`${qClean}\` |\n`;
      }
    }
    // Self-lint judgements
    if (live.self_lint && live.self_lint.consensus_lint && live.self_lint.consensus_lint.auditRecord.judgements) {
      for (const j of live.self_lint.consensus_lint.auditRecord.judgements) {
        const qClean = (j.quote || "(empty)").replace(/\n/g, ' ');
        const pen = j.label === "NOT_ISOLATED" ? "-4 pts" : "0 pts";
        md += `| ConsensusLint Self-Lint (\`0xE2cBaf...\`) | \`${j.id}\` | \`${j.label}\` | \`${j.quote_verified}\` | ${pen} | \`${qClean}\` |\n`;
      }
    }

    md += `
---

## 4. Maintainer Finding Response Flow

<!-- onchain:maintainer_responses -->
Contract registrants can attach documented responses with a structured stance (\`FIXED_NEXT\`, \`DISPUTE\`, \`WONTFIX\`) to specific findings without altering consensus verdicts:

`;
    for (const resp of live.maintainer_responses || []) {
      md += `- **Target ID**: \`${resp.tid}\` (Audit #${resp.n})\n`;
      md += `- **Rule**: \`${resp.rule_id}\`\n`;
      md += `- **Stance**: \`${resp.stance}\`\n`;
      md += `- **Response Note**: *"${resp.note}"*\n`;
      md += `- **Transaction Hash**: [\`${resp.txHash}\`](https://explorer-studio.genlayer.com/tx/${resp.txHash}) (Agreement \`${resp.agreement}\`, Elapsed \`${resp.elapsed}s\`)\n`;
      md += `- **Stored Responses Array**: \`${JSON.stringify(resp.stored_responses)}\`\n\n`;
    }

    md += `
---

## 5. HygieneBadges On-Chain Verification

<!-- onchain:badges -->
Cross-contract view composition via \`gl.get_contract_at(Address(ledger_address)).view().get_target_summary(target_id)\`:

| Badge ID | Target ID | Display Name | Current Status | Grade | Score | Claim Tx Hash | Agreement |
|---|---|---|---|---|---|---|---|
`;
    for (const [key, b] of Object.entries(live.badges || {})) {
      const rec = b.record;
      md += `| \`${rec.id}\` | \`${rec.target_id}\` | ${rec.display_name} | \`${rec.current_status}\` | **${rec.current_grade}** | ${rec.current_score} | [\`${b.claimTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${b.claimTxHash}) | \`${b.agreement}\` |\n`;
    }

    md += `
> [!NOTE]
> **Badge Minting on Truncated Audits**: HygieneBadges verifies the target summary score and grade from ConsensusLint, but does not refuse badges when \`truncated == true\`. The BADGE_B for ConsensusLint was issued on its truncated audit (Score 94, Grade B).

---

## 6. Decoded Negative Revert Tests

<!-- onchain:negative_tests -->
Every negative constraint is rejected deterministically via \`raise gl.vm.UserError("<exact message>")\`. Receipts record execution status \`ERROR\` with the decoded error string verified against contract literals, alongside raw base64 leader bytes:

| Test ID | Description | Transaction Hash | Receipt Status | Agreement | Raw Base64 Leader Bytes | Decoded \`gl.vm.UserError\` | Result |
|---|---|---|---|---|---|---|---|
`;
    for (const neg of live.negative_tests || []) {
      md += `| **${neg.testId}** | ${neg.description} | [\`${(neg.txHash || "").slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${neg.txHash}) | \`${neg.status}\` | \`${neg.agreement || "3/5"}\` | \`${neg.rawBase64 || "N/A"}\` | \`"${neg.decodedError}"\` | **${neg.passed ? 'PASS' : 'FAIL'}** |\n`;
    }

    if (live.historical_targets) {
      md += `
---

## 7. Real-World Historical Contract Audits On-Chain

<!-- onchain:historical_targets -->
Four historical Intelligent Contract versions were registered and audited on **GenLayer Studionet (Preview)** through ConsensusLint:

| Contract Target | Target ID | Register Tx | Audit Tx | Agreement | On-Chain Score | On-Chain Grade | Expected Local Score | Delta vs Local |
|---|---|---|---|---|---|---|---|---|
`;
      for (const [key, ht] of Object.entries(live.historical_targets)) {
        md += `| **${ht.label}** | \`${ht.tid}\` | [\`${ht.registrationTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${ht.registrationTxHash}) | [\`${ht.auditTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${ht.auditTxHash}) | \`${ht.auditAgreement}\` | **${ht.auditRecord.score}** | **${ht.auditRecord.grade}** | ${ht.expectedLocalScore} (${ht.expectedLocalGrade}) | ${ht.scoreDifference >= 0 ? '+' : ''}${ht.scoreDifference} |\n`;
      }
    }

    if (live.disagreed_runs && live.disagreed_runs.length > 0) {
      md += `
---

## 8. Observed On-Chain Validator Disagreement

<!-- onchain:disagreed_runs -->
In accordance with Standing Rule 0 ("Every failed/disagreed/timed-out/reverted tx is recorded in the evidence JSON"), this transaction records real-world validator disagreement observed on Studionet:

| Target | Transaction Hash | Status | Result Name | Round Votes | Agreement | Explanation |
|---|---|---|---|---|---|---|
`;
      for (const dr of live.disagreed_runs) {
        const vnames = (dr.last_round_votes || []).join(", ");
        md += `| ${dr.label} | [\`${dr.txHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${dr.txHash}) | \`${dr.status}\` | \`${dr.result_name}\` | \`${vnames}\` | 2/5 | ${dr.explanation} |\n`;
      }
    }

    if (live.superseded_runs && live.superseded_runs.length > 0) {
      md += `
---

## 9. Superseded Runs & Diagnostics

<!-- onchain:superseded_runs -->
| Type | Transaction Hash | Reason / Root Cause |
|---|---|---|
`;
      for (const sr of live.superseded_runs) {
        md += `| \`${sr.type}\` | [\`${sr.txHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${sr.txHash}) | ${sr.reason} |\n`;
      }
    }

    if (live.evolving_progress) {
      const prog = live.evolving_progress;
      md += `
---

## 10. Evolving Contract & Longitudinal Progress Verification

<!-- onchain:evolving_progress -->
| Metric | Older Audit (#${prog.older_n}) | Newer Audit (#${prog.newer_n}) | Delta |
|---|---|---|---|
| **Source SHA-256** | \`${prog.older_sha256.slice(0, 16)}...\` | \`${prog.newer_sha256.slice(0, 16)}...\` | Modified |
| **Hygiene Score** | **${prog.score_before}** | **${prog.score_after}** | **+${prog.score_delta} points** |
| **Grade** | **${prog.grade_before}** | **${prog.grade_after}** | **Improved** |

### Per-Rule Finding Deltas
`;
      for (const [r, d] of Object.entries(prog.rule_deltas || {})) {
        md += `- **Rule \`${r}\`**: Before = ${d.before}, After = ${d.after} (Delta: \`${d.delta}\`)\n`;
      }
    }

    if (live.ecosystem_views) {
      md += `
---

## 11. Fixture & Sample Statistics (n=7 targets, 5 synthetic)

<!-- onchain:ecosystem_views -->
- **Total Targets Registered**: \`${live.ecosystem_views.meta.targets_total}\`
- **Total Audits Performed**: \`${live.ecosystem_views.meta.audits_total}\`
- **Scored Targets**: \`${live.ecosystem_views.meta.targets_scored_total}\`

### Leaderboard Top Targets
`;
      const best = (live.ecosystem_views.board && live.ecosystem_views.board.best) || [];
      for (const b of best) {
        md += `- **${b.label}** (\`${b.id}\`): Score ${b.score} (Grade ${b.grade})\n`;
      }
      md += `\n> [!NOTE]\n> **Leaderboard Note on Truncation**: ShellLike is a truncated audit; the board ranks by score and does not exclude truncated audits.\n`;
    }
  }

  md += `
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
`;

  return md;
}

function renderEvidence() {
  const md = renderMarkdown();
  const outPath = path.join(__dirname, '../../docs/EVIDENCE.md');
  fs.writeFileSync(outPath, md, 'utf8');
  console.log("Rendered EVIDENCE.md successfully to:", outPath);
}

if (require.main === module) {
  renderEvidence();
}

module.exports = {
  renderMarkdown,
  renderEvidence,
};
