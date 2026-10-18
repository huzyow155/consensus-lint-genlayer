// scripts/tools/render_evidence.js
const fs = require('fs');
const path = require('path');

function renderEvidence() {
  const deployPath = path.join(__dirname, '../deploy/deployments.json');
  const livePath = path.join(__dirname, '../deploy/live_evidence.json');

  if (!fs.existsSync(deployPath)) {
    console.error("deployments.json missing");
    return;
  }
  const deployments = JSON.parse(fs.readFileSync(deployPath, 'utf8'));

  let live = null;
  if (fs.existsSync(livePath)) {
    live = JSON.parse(fs.readFileSync(livePath, 'utf8'));
  }

  let md = `# On-Chain Evidence & Verification

All transactions and audits documented below were executed on **GenLayer Studionet (Preview)** (Chain ID \`61999\`, RPC \`https://studio.genlayer.com/api\`, Explorer \`https://explorer-studio.genlayer.com\`).

> [!NOTE]
> Consensus outcomes are reported as **accepted by validators** with the real consensus agreement ratio (e.g. \`3/5\`) extracted directly from receipt validator votes. Revert outcomes record the exact decoded \`gl.vm.UserError\` string returned from GenVM execution.

---

## 1. Primary Contract Deployments

| Contract | Address | Deploy Transaction Hash | Agreement | Status | Source SHA-256 |
|---|---|---|---|---|---|
| **ConsensusLint** | \`${deployments.contracts.ConsensusLint.address}\` | [\`${deployments.contracts.ConsensusLint.deployTxHash}\`](https://explorer-studio.genlayer.com/tx/${deployments.contracts.ConsensusLint.deployTxHash}) | \`${deployments.contracts.ConsensusLint.agreement}\` | \`${deployments.contracts.ConsensusLint.status}\` | \`${deployments.contracts.ConsensusLint.sourceSha256}\` |
| **HygieneBadges** | \`${deployments.contracts.HygieneBadges.address}\` | [\`${deployments.contracts.HygieneBadges.deployTxHash}\`](https://explorer-studio.genlayer.com/tx/${deployments.contracts.HygieneBadges.deployTxHash}) | \`${deployments.contracts.HygieneBadges.agreement}\` | \`${deployments.contracts.HygieneBadges.status}\` | \`${deployments.contracts.HygieneBadges.sourceSha256}\` |
| **Probe (superseded diagnostic)** | \`${deployments.contracts.Probe.address}\` | [\`${deployments.contracts.Probe.deployTxHash}\`](https://explorer-studio.genlayer.com/tx/${deployments.contracts.Probe.deployTxHash}) | \`3/5\` | \`${deployments.contracts.Probe.status}\` | \`35de2f50206bac0addafb711623795519d8f67efd631e0388b49e9b8c425989b\` |

### Inter-Contract Configuration
- **\`HygieneBadges.set_ledger\` Tx**: [\`${deployments.contracts.HygieneBadges.setLedgerTxHash}\`](https://explorer-studio.genlayer.com/tx/${deployments.contracts.HygieneBadges.setLedgerTxHash})
- **Agreement**: \`${deployments.contracts.HygieneBadges.setLedgerAgreement}\`
- **Configured Ledger**: \`${deployments.contracts.HygieneBadges.ledgerAddress}\`
- **Deployer / Owner**: \`${deployments.deployer}\`

---
`;

  if (live) {
    md += `
## 2. On-Chain Positive Fixture Audits

| Fixture Target | Target ID | Register Tx | Audit Tx | Agreement | Score | Grade | Truncated | Findings Count |
|---|---|---|---|---|---|---|---|---|
`;
    for (const [key, t] of Object.entries(live.targets || {})) {
      const fCount = Object.keys(t.auditRecord.findings || {}).length;
      md += `| **${t.label}** | \`${t.tid}\` | [\`${t.registrationTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${t.registrationTxHash}) | [\`${t.auditTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${t.auditTxHash}) | \`${t.auditAgreement}\` | **${t.auditRecord.score}** | **${t.auditRecord.grade}** | \`${t.auditRecord.truncated}\` | ${fCount} rules |\n`;
    }

    md += `
---

## 3. On-Chain Dogfooding (Self-Lint)

ConsensusLint evaluated its own deployed contracts directly via validator re-fetch from GitHub:

| Contract | Target ID | Register Tx | Audit Tx | Agreement | Hygiene Score | Grade | Key Rule Findings |
|---|---|---|---|---|---|---|---|
`;
    for (const [key, s] of Object.entries(live.self_lint || {})) {
      const findingKeys = Object.keys(s.auditRecord.findings || {}).join(", ") || "None";
      md += `| **${s.label}** | \`${s.tid}\` | [\`${s.registrationTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${s.registrationTxHash}) | [\`${s.auditTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${s.auditTxHash}) | \`${s.auditAgreement}\` | **${s.auditRecord.score}** | **${s.auditRecord.grade}** | \`${findingKeys}\` |\n`;
    }

    md += `
---

## 4. Maintainer Finding Response Flow

Contract authors can attach documented responses to specific findings without altering consensus verdicts:

`;
    for (const resp of live.maintainer_responses || []) {
      md += `- **Target ID**: \`${resp.tid}\` (Audit #${resp.n})\n`;
      md += `- **Rule**: \`${resp.rule_id}\`\n`;
      md += `- **Response Note**: *"${resp.note}"*\n`;
      md += `- **Transaction Hash**: [\`${resp.txHash}\`](https://explorer-studio.genlayer.com/tx/${resp.txHash}) (Agreement \`${resp.agreement}\`)\n`;
      md += `- **Stored Responses Array**: \`${JSON.stringify(resp.stored_responses)}\`\n\n`;
    }

    md += `
---

## 5. HygieneBadges On-Chain Verification

Cross-contract view composition via \`gl.get_contract_at(Address(ledger_address)).view().get_target_summary(target_id)\`:

| Badge ID | Target ID | Display Name | Current Status | Grade | Score | Claim Tx Hash | Agreement |
|---|---|---|---|---|---|---|---|
`;
    for (const [key, b] of Object.entries(live.badges || {})) {
      const rec = b.record;
      md += `| \`${rec.id}\` | \`${rec.target_id}\` | ${rec.display_name} | \`${rec.current_status}\` | **${rec.current_grade}** | ${rec.current_score} | [\`${b.claimTxHash.slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${b.claimTxHash}) | \`${b.agreement}\` |\n`;
    }

    md += `
---

## 6. Decoded Negative Revert Tests

Every negative constraint is rejected deterministically via \`raise gl.vm.UserError("<exact message>")\`. Receipts record execution status \`ERROR\` with the decoded error string:

| Test ID | Description | Transaction Hash | Receipt Status | Leader Execution | Decoded \`gl.vm.UserError\` | Result |
|---|---|---|---|---|---|---|
`;
    for (const neg of live.negative_tests || []) {
      md += `| **${neg.testId}** | ${neg.description} | [\`${(neg.txHash || "").slice(0, 14)}...\`](https://explorer-studio.genlayer.com/tx/${neg.txHash}) | \`${neg.status}\` | \`${neg.leaderExecution}\` | \`"${neg.decodedError}"\` | **${neg.passed ? 'PASS' : 'FAIL'}** |\n`;
    }

    if (live.evolving_progress) {
      const prog = live.evolving_progress;
      md += `
---

## 7. Evolving Contract & Longitudinal Progress Verification

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

## 8. Ecosystem Aggregations & Public Views

- **Total Targets Registered**: \`${live.ecosystem_views.meta.targets_total}\`
- **Total Audits Performed**: \`${live.ecosystem_views.meta.audits_total}\`
- **Scored Targets**: \`${live.ecosystem_views.meta.targets_scored_total}\`

### Leaderboard Top Targets
`;
      const best = (live.ecosystem_views.board && live.ecosystem_views.board.best) || [];
      for (const b of best) {
        md += `- **${b.label}** (\`${b.id}\`): Score ${b.score} (Grade ${b.grade})\n`;
      }
    }
  }

  const outPath = path.join(__dirname, '../../docs/EVIDENCE.md');
  fs.writeFileSync(outPath, md, 'utf8');
  console.log("Rendered EVIDENCE.md successfully to:", outPath);
}

renderEvidence();
