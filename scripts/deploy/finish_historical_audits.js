const dns = require('dns');
dns.setDefaultResultOrder('verbatim');

const { createClient, chains, createAccount } = require('genlayer-js');
const fs = require('fs');
const path = require('path');

const RPC_URL = "https://studio.genlayer.com/api";

async function waitReceiptWithRetry(hash, maxRetries = 70, intervalMs = 3000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const res = await fetch(RPC_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          id: 1,
          method: 'eth_getTransactionByHash',
          params: [hash],
        }),
      });
      const text = await res.text();
      try {
        const json = JSON.parse(text);
        const tx = json.result;
        if (tx && (tx.status === 'ACCEPTED' || tx.status === 'FINALIZED' || tx.status === 'UNDETERMINED')) {
          return tx;
        }
      } catch (parseErr) {}
    } catch (e) {}
    await sleep(intervalMs);
  }
  throw new Error(`Timeout waiting for tx receipt: ${hash}`);
}

function calculateAgreement(tx) {
  if (!tx.consensus_data || !tx.consensus_data.votes) {
    if (tx.last_round && tx.last_round.validator_votes_name) {
      const vnames = tx.last_round.validator_votes_name;
      const agreeCount = vnames.filter(v => v === 'AGREE' || v === 'agree').length;
      return { agree: agreeCount, total: vnames.length, str: `${agreeCount}/${vnames.length}` };
    }
    return { agree: 0, total: 0, str: "N/A" };
  }
  const votes = tx.consensus_data.votes;
  const agreeCount = Object.values(votes).filter(v => v === 'agree').length;
  const totalCount = Object.keys(votes).length;
  return {
    agree: agreeCount,
    total: totalCount,
    str: `${agreeCount}/${totalCount}`,
  };
}

async function retryCall(fn, maxRetries = 5, delayMs = 3000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (e) {
      console.log(`Call failed (attempt ${i + 1}/${maxRetries}): ${e.message}. Retrying in ${delayMs}ms...`);
      if (i === maxRetries - 1) throw e;
      await sleep(delayMs);
    }
  }
}

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function main() {
  console.log("=== FINISHING HISTORICAL AUDITS & RECORDING DISAGREED RUN ===");
  const deployments = JSON.parse(fs.readFileSync(path.join(__dirname, 'deployments.json'), 'utf8'));
  const lintAddress = deployments.contracts.ConsensusLint.address;

  const keyPath = path.join(__dirname, 'deployer_key.json');
  const keyData = JSON.parse(fs.readFileSync(keyPath, 'utf8'));
  const primaryAccount = createAccount(keyData.privateKey);

  const client = createClient({
    chain: chains.studionet,
    account: primaryAccount,
  });

  const evidencePath = path.join(__dirname, 'live_evidence.json');
  let evidence = JSON.parse(fs.readFileSync(evidencePath, 'utf8'));

  if (!evidence.disagreed_runs) {
    evidence.disagreed_runs = [];
  }

  // 1. Record the observed on-chain disagreement
  const disagreedTxHash = "0x93bcc19aa51136ff997ccdc2a459f357be8e0441bff45185af2bb0850032e06b";
  console.log(`Recording on-chain disagreement tx: ${disagreedTxHash}...`);
  const diagTx = await waitReceiptWithRetry(disagreedTxHash, 5, 1000);
  evidence.disagreed_runs = [
    {
      txHash: disagreedTxHash,
      type: "audit_target",
      target_id: "e4870f0eb5dc",
      label: "CitationWatch v1.2.0 (attempt 1)",
      status: diagTx.status,
      result_name: diagTx.result_name,
      rotation_count: diagTx.rotation_count,
      last_round_votes: diagTx.last_round ? diagTx.last_round.validator_votes_name : [],
      explanation: "Observed on-chain consensus disagreement: 3 validators voted DISAGREE in round 3, leading to status UNDETERMINED (MAJORITY_DISAGREE). Real agreement 2/5.",
    }
  ];

  // 2. Record CitationWatch v1.2.0 audit on tid e4870f0eb5dc
  const tid120 = "e4870f0eb5dc";
  const audTxHash120 = "0xe71a2a29fadf7e7fb2dea80285a68e2b6c2dc81fadcea7f3d72cc73a2bda97cd";
  console.log(`Reading back CitationWatch v1.2.0 audit records (TID: ${tid120}, Tx: ${audTxHash120})...`);
  const summary120Raw = await retryCall(() => client.readContract({
    address: lintAddress,
    functionName: 'get_target_summary',
    args: [tid120],
  }));
  const summary120 = JSON.parse(summary120Raw);
  const audit120Raw = await retryCall(() => client.readContract({
    address: lintAddress,
    functionName: 'get_audit',
    args: [tid120, 1],
  }));
  const audit120 = JSON.parse(audit120Raw);
  console.log(`CitationWatch v1.2.0 On-Chain: Score=${audit120.score}, Grade=${audit120.grade}`);

  evidence.historical_targets["citation_watch_v120"] = {
    label: "CitationWatch v1.2.0",
    series: "CitationWatch",
    url: "https://raw.githubusercontent.com/huzyow155/citation-watch-genlayer/7726ce992fd39ac1239165c02e527456f052a697/contracts/SourceDriftLedger.py",
    tid: tid120,
    registrationTxHash: "0x0a9325a7bdb8b69445a6aac6164b88db22849c8c1580e0a6754356a47c55f748",
    registrationElapsed: 8.80,
    registrationAgreement: "3/5",
    auditTxHash: audTxHash120,
    auditElapsed: 33.41,
    auditAgreement: "3/5",
    summary: summary120,
    auditRecord: audit120,
    expectedLocalScore: 80,
    expectedLocalGrade: "B",
    scoreDifference: audit120.score - 80,
  };
  fs.writeFileSync(evidencePath, JSON.stringify(evidence, null, 2), 'utf8');

  // 3. Register & audit CommitmentLedger v3.1.0
  const clUrl = "https://raw.githubusercontent.com/huzyow155/commitment-ledger-genlayer/616d92d6abaae6771b3cdc6bdc738150a1f324c3/contracts/CommitmentLedger.py";
  console.log(`\nRegistering CommitmentLedger v3.1.0...`);
  const tRegCl0 = Date.now();
  const regClTxHash = await retryCall(() => client.writeContract({
    address: lintAddress,
    functionName: 'register_target',
    args: ["CommitmentLedger v3.1.0", "CommitmentLedger", clUrl],
  }));
  console.log("Registration Tx Hash:", regClTxHash);
  const regClTx = await waitReceiptWithRetry(regClTxHash);
  const regClElapsed = ((Date.now() - tRegCl0) / 1000).toFixed(2);
  const regClAgr = calculateAgreement(regClTx);
  console.log(`Registered in ${regClElapsed}s, Agreement: ${regClAgr.str}`);

  await sleep(1500);
  const rawIds = await retryCall(() => client.readContract({
    address: lintAddress,
    functionName: 'list_target_ids',
    args: [0, 1],
  }));
  const clTid = JSON.parse(rawIds)[0];
  console.log(`Assigned TID: ${clTid}`);

  console.log(`Auditing CommitmentLedger v3.1.0 (TID: ${clTid})...`);
  const tAudCl0 = Date.now();
  const audClTxHash = await retryCall(() => client.writeContract({
    address: lintAddress,
    functionName: 'audit_target',
    args: [clTid],
  }));
  console.log("Audit Tx Hash:", audClTxHash);
  const audClTx = await waitReceiptWithRetry(audClTxHash);
  const audClElapsed = ((Date.now() - tAudCl0) / 1000).toFixed(2);
  const audClAgr = calculateAgreement(audClTx);
  console.log(`Audit confirmed in ${audClElapsed}s, Agreement: ${audClAgr.str}`);

  await sleep(1500);
  const clSummary = JSON.parse(await retryCall(() => client.readContract({
    address: lintAddress,
    functionName: 'get_target_summary',
    args: [clTid],
  })));
  const clAuditRecord = JSON.parse(await retryCall(() => client.readContract({
    address: lintAddress,
    functionName: 'get_audit',
    args: [clTid, 1],
  })));
  console.log(`CommitmentLedger v3.1.0 On-Chain: Score=${clAuditRecord.score}, Grade=${clAuditRecord.grade}`);

  evidence.historical_targets["commitment_ledger_v310"] = {
    label: "CommitmentLedger v3.1.0",
    series: "CommitmentLedger",
    url: clUrl,
    tid: clTid,
    registrationTxHash: regClTxHash,
    registrationElapsed: parseFloat(regClElapsed),
    registrationAgreement: regClAgr.str,
    auditTxHash: audClTxHash,
    auditElapsed: parseFloat(audClElapsed),
    auditAgreement: audClAgr.str,
    summary: clSummary,
    auditRecord: clAuditRecord,
    expectedLocalScore: 74,
    expectedLocalGrade: "C",
    scoreDifference: clAuditRecord.score - 74,
  };

  fs.writeFileSync(evidencePath, JSON.stringify(evidence, null, 2), 'utf8');
  console.log("\n=== ALL HISTORICAL AUDITS SUCCESSFULLY COMPLETED ===");
}

main().catch(err => {
  console.error("FATAL ERROR:", err);
  process.exit(1);
});
