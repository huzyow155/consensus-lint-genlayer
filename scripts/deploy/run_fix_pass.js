const dns = require('dns');
dns.setDefaultResultOrder('verbatim');

const { createClient, chains, createAccount } = require('genlayer-js');
const { generatePrivateKey } = require('viem/accounts');
const fs = require('fs');
const path = require('path');

const RPC_URL = "https://studio.genlayer.com/api";

async function waitReceiptWithRetry(hash, maxRetries = 60, intervalMs = 3000) {
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
        if (tx && (tx.status === 'ACCEPTED' || tx.status === 'FINALIZED')) {
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

function decodeUserErrorWithRaw(tx) {
  try {
    const leader = tx.consensus_data && tx.consensus_data.leader_receipt && tx.consensus_data.leader_receipt[0];
    if (leader && leader.result) {
      const rawBase64 = leader.result;
      const buf = Buffer.from(rawBase64, 'base64');
      let decoded = "";
      if (buf.length > 0 && buf[0] === 1) {
        decoded = buf.slice(1).toString('utf8');
      } else {
        decoded = buf.toString('utf8');
      }
      return {
        decodedError: decoded,
        rawBase64: rawBase64,
        rawHex: buf.toString('hex'),
        leaderExecution: leader.execution_result || "ERROR",
      };
    }
  } catch (e) {}
  return {
    decodedError: "Unknown execution error",
    rawBase64: "",
    rawHex: "",
    leaderExecution: "ERROR",
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
  console.log("=== RUNNING CONSENSUSLINT EVIDENCE INTEGRITY FIX PASS ===");
  console.log("Network: GenLayer Studionet (Preview)");
  console.log("Chain ID: 61999");
  console.log("RPC:", RPC_URL);

  const deployments = JSON.parse(fs.readFileSync(path.join(__dirname, 'deployments.json'), 'utf8'));
  const lintAddress = deployments.contracts.ConsensusLint.address;
  const badgesAddress = deployments.contracts.HygieneBadges.address;
  console.log("ConsensusLint address:", lintAddress);
  console.log("HygieneBadges address:", badgesAddress);

  const keyPath = path.join(__dirname, 'deployer_key.json');
  const keyData = JSON.parse(fs.readFileSync(keyPath, 'utf8'));
  const primaryAccount = createAccount(keyData.privateKey);
  console.log("Primary deployer account:", primaryAccount.address);

  const strangerKey = generatePrivateKey();
  const strangerAccount = createAccount(strangerKey);
  console.log("Stranger account for security tests:", strangerAccount.address);

  const client = createClient({
    chain: chains.studionet,
    account: primaryAccount,
  });

  const strangerClient = createClient({
    chain: chains.studionet,
    account: strangerAccount,
  });

  const evidencePath = path.join(__dirname, 'live_evidence.json');
  let evidence = JSON.parse(fs.readFileSync(evidencePath, 'utf8'));

  function saveEvidence() {
    fs.writeFileSync(evidencePath, JSON.stringify(evidence, null, 2), 'utf8');
  }

  // 1. Maintainer Response (F1)
  console.log("\n==========================================");
  console.log("=== STEP 1: FIX MAINTAINER RESPONSE (F1) ===");
  console.log("==========================================");

  const badTid = evidence.targets.bad_contract.tid;
  console.log(`Submitting valid maintainer response to bad_contract (TID: ${badTid}, audit #1)...`);
  const tResp0 = Date.now();
  const respTxHash = await retryCall(() => client.writeContract({
    address: lintAddress,
    functionName: 'respond_to_finding',
    args: [
      badTid,
      1,
      'CL05',
      'FIXED_NEXT',
      'Acknowledged: TreeMap lazy initialization will be adopted in next patch.'
    ],
  }));
  console.log("Response Tx Hash:", respTxHash);
  const respTx = await waitReceiptWithRetry(respTxHash);
  const respElapsed = ((Date.now() - tResp0) / 1000).toFixed(2);
  const respAgr = calculateAgreement(respTx);
  console.log(`Response accepted in ${respElapsed}s, Agreement: ${respAgr.str}`);

  await sleep(1500);
  const updatedBadAuditRaw = await client.readContract({
    address: lintAddress,
    functionName: 'get_audit',
    args: [badTid, 1],
  });
  const updatedBadAudit = JSON.parse(updatedBadAuditRaw);
  console.log("Updated audit responses:", JSON.stringify(updatedBadAudit.responses, null, 2));

  // Move old failed runs to superseded_runs
  if (!evidence.superseded_runs) {
    evidence.superseded_runs = [];
  }
  for (const oldResp of evidence.maintainer_responses || []) {
    evidence.superseded_runs.push({
      type: "maintainer_response",
      txHash: oldResp.txHash,
      reason: "Called with 4 arguments; leader execution ERROR; nothing stored",
      originalData: oldResp,
    });
  }

  evidence.maintainer_responses = [
    {
      tid: badTid,
      n: 1,
      rule_id: 'CL05',
      stance: 'FIXED_NEXT',
      note: 'Acknowledged: TreeMap lazy initialization will be adopted in next patch.',
      txHash: respTxHash,
      elapsed: parseFloat(respElapsed),
      agreement: respAgr.str,
      stored_responses: updatedBadAudit.responses,
    }
  ];
  saveEvidence();
  console.log("Maintainer response successfully recorded!");

  // 2. Negative Tests (F2)
  console.log("\n==========================================");
  console.log("=== STEP 2: NEGATIVE TESTS & RE-RUN NEG-04 ===");
  console.log("==========================================");

  async function executeNegativeTest(testId, description, expectedPattern, writePromise) {
    console.log(`\nExecuting ${testId}: ${description}...`);
    const t0 = Date.now();
    let txHash;
    try {
      txHash = await retryCall(writePromise);
    } catch (e) {
      console.log(`Client threw pre-tx error: ${e.message}`);
      return;
    }
    console.log("Tx Hash:", txHash);
    const tx = await waitReceiptWithRetry(txHash);
    const elapsed = ((Date.now() - t0) / 1000).toFixed(2);
    const agr = calculateAgreement(tx);
    const decoded = decodeUserErrorWithRaw(tx);
    const passed = decoded.decodedError.includes(expectedPattern);
    console.log(`${testId} Result: status=${tx.status}, agr=${agr.str}, leader=${decoded.leaderExecution}, decoded="${decoded.decodedError}", rawBase64="${decoded.rawBase64}"`);
    console.log(`Passed: ${passed}`);

    return {
      testId,
      description,
      txHash,
      status: tx.status,
      agreement: agr.str,
      elapsed: parseFloat(elapsed),
      leaderExecution: decoded.leaderExecution,
      rawBase64: decoded.rawBase64,
      rawHex: decoded.rawHex,
      decodedError: decoded.decodedError,
      expectedPattern,
      passed,
    };
  }

  // Re-run NEG-04: Non-registrant attempt with 5 arguments
  const neg04 = await executeNegativeTest(
    "NEG-04",
    "Reject finding response from non-registrant sender",
    "only the registrant can do this",
    () => strangerClient.writeContract({
      address: lintAddress,
      functionName: 'respond_to_finding',
      args: [
        badTid,
        1,
        'CL05',
        'FIXED_NEXT',
        'Unauthorized intruder response attempt.'
      ],
    })
  );

  // NEG-06: Invalid stance test
  const neg06 = await executeNegativeTest(
    "NEG-06",
    "Reject finding response with invalid stance",
    "invalid stance",
    () => client.writeContract({
      address: lintAddress,
      functionName: 'respond_to_finding',
      args: [
        badTid,
        1,
        'CL05',
        'MAYBE',
        'Unauthorized stance attempt test.'
      ],
    })
  );

  // NEG-07: Finding not in audit
  const neg07 = await executeNegativeTest(
    "NEG-07",
    "Reject finding response for rule not present in audit",
    "finding not present in audit",
    () => client.writeContract({
      address: lintAddress,
      functionName: 'respond_to_finding',
      args: [
        badTid,
        1,
        'CL04',
        'FIXED_NEXT',
        'Unauthorized rule finding attempt.'
      ],
    })
  );

  // Backfill raw base64 for NEG-01, NEG-02, NEG-03, NEG-05 from existing receipts
  const updatedNegatives = [];
  for (const n of evidence.negative_tests) {
    if (n.testId === "NEG-04") {
      // Replace with new valid NEG-04
      updatedNegatives.push(neg04);
    } else {
      console.log(`Backfilling raw receipt data for ${n.testId} (${n.txHash})...`);
      try {
        const tx = await waitReceiptWithRetry(n.txHash, 5, 1000);
        const dec = decodeUserErrorWithRaw(tx);
        updatedNegatives.push({
          ...n,
          rawBase64: dec.rawBase64,
          rawHex: dec.rawHex,
        });
      } catch (e) {
        console.log(`Failed to fetch receipt for ${n.testId}: ${e.message}`);
        updatedNegatives.push(n);
      }
    }
  }
  if (neg06) updatedNegatives.push(neg06);
  if (neg07) updatedNegatives.push(neg07);

  evidence.negative_tests = updatedNegatives;
  saveEvidence();
  console.log("Negative tests successfully updated!");

  // 3. Historical Repos Registration and On-chain Audits
  console.log("\n==========================================");
  console.log("=== STEP 3: HISTORICAL REPOS REGISTRATION & AUDITS ===");
  console.log("==========================================");

  if (!evidence.historical_targets) {
    evidence.historical_targets = {};
  }

  const historicalTargets = [
    {
      key: "citation_watch_v100",
      label: "CitationWatch v1.0.0",
      series: "CitationWatch",
      url: "https://raw.githubusercontent.com/huzyow155/citation-watch-genlayer/db7efa656f3ceb14d40b3607f1037fdcbcfdf6ef/contracts/SourceDriftLedger.py",
      expectedLocalScore: 59,
      expectedLocalGrade: "D",
    },
    {
      key: "citation_watch_v110",
      label: "CitationWatch v1.1.0",
      series: "CitationWatch",
      url: "https://raw.githubusercontent.com/huzyow155/citation-watch-genlayer/fe0e1b82bf9dc51b1dbb2c7ad61fc4cb3883971a/contracts/SourceDriftLedger.py",
      expectedLocalScore: 83,
      expectedLocalGrade: "B",
    },
    {
      key: "citation_watch_v120",
      label: "CitationWatch v1.2.0",
      series: "CitationWatch",
      url: "https://raw.githubusercontent.com/huzyow155/citation-watch-genlayer/7726ce992fd39ac1239165c02e527456f052a697/contracts/SourceDriftLedger.py",
      expectedLocalScore: 80,
      expectedLocalGrade: "B",
    },
    {
      key: "commitment_ledger_v310",
      label: "CommitmentLedger v3.1.0",
      series: "CommitmentLedger",
      url: "https://raw.githubusercontent.com/huzyow155/commitment-ledger-genlayer/616d92d6abaae6771b3cdc6bdc738150a1f324c3/contracts/CommitmentLedger.py",
      expectedLocalScore: 74,
      expectedLocalGrade: "C",
    },
  ];

  for (const ht of historicalTargets) {
    if (evidence.historical_targets[ht.key] && evidence.historical_targets[ht.key].auditTxHash) {
      console.log(`Historical target ${ht.label} already audited (TID: ${evidence.historical_targets[ht.key].tid})`);
      continue;
    }

    console.log(`\nRegistering historical target: ${ht.label}...`);
    const tReg0 = Date.now();
    const regTxHash = await retryCall(() => client.writeContract({
      address: lintAddress,
      functionName: 'register_target',
      args: [ht.label, ht.series, ht.url],
    }));
    console.log("Registration Tx Hash:", regTxHash);
    const regTx = await waitReceiptWithRetry(regTxHash);
    const regElapsed = ((Date.now() - tReg0) / 1000).toFixed(2);
    const regAgr = calculateAgreement(regTx);
    console.log(`Registered in ${regElapsed}s, Agreement: ${regAgr.str}`);

    await sleep(1500);
    const rawIds = await retryCall(() => client.readContract({
      address: lintAddress,
      functionName: 'list_target_ids',
      args: [0, 1],
    }));
    const ids = JSON.parse(rawIds);
    const tid = ids[0];
    console.log(`Assigned TID: ${tid}`);

    console.log(`Auditing historical target ${ht.label} (TID: ${tid})...`);
    const tAud0 = Date.now();
    const audTxHash = await retryCall(() => client.writeContract({
      address: lintAddress,
      functionName: 'audit_target',
      args: [tid],
    }));
    console.log("Audit Tx Hash:", audTxHash);
    const audTx = await waitReceiptWithRetry(audTxHash);
    const audElapsed = ((Date.now() - tAud0) / 1000).toFixed(2);
    const audAgr = calculateAgreement(audTx);
    console.log(`Audit confirmed in ${audElapsed}s, Agreement: ${audAgr.str}`);

    await sleep(1500);
    const rawSummary = await retryCall(() => client.readContract({
      address: lintAddress,
      functionName: 'get_target_summary',
      args: [tid],
    }));
    const summary = JSON.parse(rawSummary);

    const rawAudit = await retryCall(() => client.readContract({
      address: lintAddress,
      functionName: 'get_audit',
      args: [tid, 1],
    }));
    const auditRecord = JSON.parse(rawAudit);

    console.log(`On-chain Result: Score=${auditRecord.score}, Grade=${auditRecord.grade}, Truncated=${auditRecord.truncated}`);
    console.log(`Local Expected: Score=${ht.expectedLocalScore}, Grade=${ht.expectedLocalGrade}`);

    evidence.historical_targets[ht.key] = {
      label: ht.label,
      series: ht.series,
      url: ht.url,
      tid,
      registrationTxHash: regTxHash,
      registrationElapsed: parseFloat(regElapsed),
      registrationAgreement: regAgr.str,
      auditTxHash: audTxHash,
      auditElapsed: parseFloat(audElapsed),
      auditAgreement: audAgr.str,
      summary,
      auditRecord,
      expectedLocalScore: ht.expectedLocalScore,
      expectedLocalGrade: ht.expectedLocalGrade,
      scoreDifference: auditRecord.score - ht.expectedLocalScore,
    };
    saveEvidence();
    await sleep(2000);
  }

  console.log("\n=== FIX PASS COMPLETED SUCCESSFULLY ===");
}

main().catch(err => {
  console.error("FATAL ERROR IN FIX PASS:", err);
  process.exit(1);
});
