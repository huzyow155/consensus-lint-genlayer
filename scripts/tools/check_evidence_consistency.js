// scripts/tools/check_evidence_consistency.js
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function checkHexAddress(addr, label) {
  if (typeof addr !== 'string' || !/^0x[0-9a-fA-F]{40}$/.test(addr)) {
    throw new Error(`Invalid address format for ${label}: ${addr}`);
  }
}

function checkTxHash(hash, label) {
  if (typeof hash !== 'string' || !/^0x[0-9a-fA-F]{64}$/.test(hash)) {
    throw new Error(`Invalid tx hash format for ${label}: ${hash}`);
  }
}

function checkAgreement(agr, label) {
  if (typeof agr !== 'string' || !/^\d+\/\d+$/.test(agr)) {
    throw new Error(`Invalid agreement format for ${label}: ${agr}`);
  }
}

function main() {
  console.log("=== CHECKING EVIDENCE CONSISTENCY ===");
  const deployPath = path.join(__dirname, '../deploy/deployments.json');
  if (!fs.existsSync(deployPath)) {
    console.log("deployments.json not yet created.");
    return;
  }
  const deployments = JSON.parse(fs.readFileSync(deployPath, 'utf8'));

  console.log("1. Checking deployments.json...");
  checkHexAddress(deployments.deployer, "deployer");
  checkHexAddress(deployments.contracts.ConsensusLint.address, "ConsensusLint.address");
  checkTxHash(deployments.contracts.ConsensusLint.deployTxHash, "ConsensusLint.deployTxHash");
  checkAgreement(deployments.contracts.ConsensusLint.agreement, "ConsensusLint.agreement");

  checkHexAddress(deployments.contracts.HygieneBadges.address, "HygieneBadges.address");
  checkTxHash(deployments.contracts.HygieneBadges.deployTxHash, "HygieneBadges.deployTxHash");
  checkAgreement(deployments.contracts.HygieneBadges.agreement, "HygieneBadges.agreement");

  checkTxHash(deployments.contracts.HygieneBadges.setLedgerTxHash, "HygieneBadges.setLedgerTxHash");
  checkAgreement(deployments.contracts.HygieneBadges.setLedgerAgreement, "HygieneBadges.setLedgerAgreement");

  // Verify contract SHA-256 matches actual file on disk
  const lintFile = path.join(__dirname, '../../contracts/ConsensusLint.py');
  const lintCode = fs.readFileSync(lintFile, 'utf8');
  const lintSha = crypto.createHash('sha256').update(lintCode, 'utf8').digest('hex');
  if (lintSha !== deployments.contracts.ConsensusLint.sourceSha256) {
    throw new Error(`ConsensusLint SHA256 mismatch: disk=${lintSha}, deployment=${deployments.contracts.ConsensusLint.sourceSha256}`);
  }

  const badgesFile = path.join(__dirname, '../../contracts/HygieneBadges.py');
  const badgesCode = fs.readFileSync(badgesFile, 'utf8');
  const badgesSha = crypto.createHash('sha256').update(badgesCode, 'utf8').digest('hex');
  if (badgesSha !== deployments.contracts.HygieneBadges.sourceSha256) {
    throw new Error(`HygieneBadges SHA256 mismatch: disk=${badgesSha}, deployment=${deployments.contracts.HygieneBadges.sourceSha256}`);
  }
  console.log("Contract SHA-256 verification: MATCH OK");

  // Check live_evidence.json if present
  const livePath = path.join(__dirname, '../deploy/live_evidence.json');
  if (fs.existsSync(livePath)) {
    console.log("\n2. Checking live_evidence.json...");
    const live = JSON.parse(fs.readFileSync(livePath, 'utf8'));
    
    // Check targets
    for (const [key, t] of Object.entries(live.targets || {})) {
      console.log(`Checking target: ${key}`);
      checkTxHash(t.registrationTxHash, `${key}.registrationTxHash`);
      checkTxHash(t.auditTxHash, `${key}.auditTxHash`);
      checkAgreement(t.registrationAgreement, `${key}.registrationAgreement`);
      checkAgreement(t.auditAgreement, `${key}.auditAgreement`);
      if (typeof t.tid !== 'string' || t.tid.length !== 12) {
        throw new Error(`Invalid target ID for ${key}: ${t.tid}`);
      }
    }

    // Check self lint
    for (const [key, s] of Object.entries(live.self_lint || {})) {
      console.log(`Checking self-lint: ${key}`);
      checkTxHash(s.registrationTxHash, `self_lint.${key}.registrationTxHash`);
      checkTxHash(s.auditTxHash, `self_lint.${key}.auditTxHash`);
      checkAgreement(s.registrationAgreement, `self_lint.${key}.registrationAgreement`);
      checkAgreement(s.auditAgreement, `self_lint.${key}.auditAgreement`);
    }

    // Check negative tests
    for (const n of live.negative_tests || []) {
      console.log(`Checking negative test: ${n.testId}`);
      if (n.txHash) checkTxHash(n.txHash, `negative_test.${n.testId}.txHash`);
      if (!n.passed) {
        throw new Error(`Negative test ${n.testId} did not pass!`);
      }
    }
    console.log("All live evidence checks: PASSED OK");
  } else {
    console.log("live_evidence.json not yet available (run in progress).");
  }

  console.log("\nALL EVIDENCE CONSISTENCY CHECKS PASSED!");
}

main();
