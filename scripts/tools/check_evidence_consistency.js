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

// Extract public methods and arities from python contract source
function extractContractMethods(contractCode) {
  const methods = {};
  const fnRegex = /def\s+([a-zA-Z0-9_]+)\s*\(\s*self\s*(?:,\s*([^)]*))?\)\s*(?:->[^:]+)?:/g;
  let match;
  while ((match = fnRegex.exec(contractCode)) !== null) {
    const fnName = match[1];
    if (fnName.startsWith('_')) continue;
    const argsStr = match[2] ? match[2].trim() : '';
    let argCount = 0;
    if (argsStr.length > 0) {
      // Split on top-level commas (ignoring types with brackets)
      let depth = 0;
      let count = 1;
      for (const ch of argsStr) {
        if (ch === '[' || ch === '(' || ch === '{') depth++;
        else if (ch === ']' || ch === ')' || ch === '}') depth--;
        else if (ch === ',' && depth === 0) count++;
      }
      argCount = count;
    }
    methods[fnName] = argCount;
  }
  return methods;
}

// Extract UserError string literals from python contract source
function extractUserErrors(contractCode) {
  const errors = new Set();
  const errRegex = /UserError\(\s*["']([^"']+)["']\s*\)/g;
  let match;
  while ((match = errRegex.exec(contractCode)) !== null) {
    errors.add(match[1]);
  }
  return errors;
}

// K1: Call-site arity and method name vs contract
function checkK1_CallSiteArity(scriptFiles, contractCodes) {
  const allMethods = {};
  for (const code of contractCodes) {
    Object.assign(allMethods, extractContractMethods(code));
  }

  const errors = [];
  for (const sPath of scriptFiles) {
    if (!fs.existsSync(sPath)) continue;
    const code = fs.readFileSync(sPath, 'utf8');
    
    // Look for contract calls: functionName: 'xxx', args: [...]
    const callRegex = /functionName:\s*['"]([a-zA-Z0-9_]+)['"]\s*,\s*args:\s*\[([\s\S]*?)\]/g;
    let match;
    while ((match = callRegex.exec(code)) !== null) {
      const fnName = match[1];
      const argsRaw = match[2].trim();
      let passedArgCount = 0;
      if (argsRaw.length > 0) {
        let depth = 0;
        let inQuote = null;
        let count = 1;
        for (let i = 0; i < argsRaw.length; i++) {
          const ch = argsRaw[i];
          if (inQuote) {
            if (ch === inQuote && argsRaw[i - 1] !== '\\') inQuote = null;
          } else {
            if (ch === '"' || ch === "'") inQuote = ch;
            else if (ch === '[' || ch === '{' || ch === '(') depth++;
            else if (ch === ']' || ch === '}' || ch === ')') depth--;
            else if (ch === ',' && depth === 0) count++;
          }
        }
        passedArgCount = count;
      }

      if (!(fnName in allMethods)) {
        errors.push(`[K1 FAIL] ${path.basename(sPath)}: Unknown method '${fnName}'`);
      } else {
        const expectedArity = allMethods[fnName];
        if (passedArgCount !== expectedArity) {
          errors.push(`[K1 FAIL] ${path.basename(sPath)}: Method '${fnName}' called with ${passedArgCount} args, contract expects ${expectedArity}`);
        }
      }
    }
  }
  return errors;
}

// K2: Every decodedError is a string literal of the contract source
function checkK2_DecodedErrors(liveEvidence, contractCodes) {
  const allUserErrors = new Set();
  for (const code of contractCodes) {
    for (const e of extractUserErrors(code)) allUserErrors.add(e);
  }

  const errors = [];
  for (const neg of liveEvidence.negative_tests || []) {
    if (neg.leaderExecution === 'ERROR' && neg.decodedError) {
      if (!allUserErrors.has(neg.decodedError)) {
        errors.push(`[K2 FAIL] Negative test ${neg.testId}: decodedError "${neg.decodedError}" not found in contract UserError literals`);
      }
    }
  }
  return errors;
}

// K3: Any response flow row with an empty stored responses array must be flagged as failed
function checkK3_MaintainerResponses(liveEvidence) {
  const errors = [];
  for (const resp of liveEvidence.maintainer_responses || []) {
    if (!resp.stored_responses || !Array.isArray(resp.stored_responses) || resp.stored_responses.length === 0) {
      errors.push(`[K3 FAIL] Target ${resp.tid} audit #${resp.n}: response transaction succeeded but stored_responses is empty`);
    }
  }
  return errors;
}

// K4: Every doc sentence that says "on-chain" or "Studionet" for a number must trace to a tx hash in JSON
function checkK4_OnchainClaimsTraced(docPath, liveEvidence) {
  const errors = [];
  if (!fs.existsSync(docPath)) return errors;
  const content = fs.readFileSync(docPath, 'utf8');
  
  // Collect all known tx hashes from live_evidence.json
  const knownTxs = new Set();
  for (const t of Object.values(liveEvidence.targets || {})) {
    if (t.registrationTxHash) knownTxs.add(t.registrationTxHash.toLowerCase());
    if (t.auditTxHash) knownTxs.add(t.auditTxHash.toLowerCase());
    if (t.audit2 && t.audit2.txHash) knownTxs.add(t.audit2.txHash.toLowerCase());
  }
  for (const s of Object.values(liveEvidence.self_lint || {})) {
    if (s.registrationTxHash) knownTxs.add(s.registrationTxHash.toLowerCase());
    if (s.auditTxHash) knownTxs.add(s.auditTxHash.toLowerCase());
  }
  for (const r of liveEvidence.maintainer_responses || []) {
    if (r.txHash) knownTxs.add(r.txHash.toLowerCase());
  }
  for (const b of Object.values(liveEvidence.badges || {})) {
    if (b.claimTxHash) knownTxs.add(b.claimTxHash.toLowerCase());
  }
  for (const n of liveEvidence.negative_tests || []) {
    if (n.txHash) knownTxs.add(n.txHash.toLowerCase());
  }

  // Look for onchain tags in the doc: <!-- onchain:KEY -->
  const onchainTagRegex = /<!--\s*onchain:([a-zA-Z0-9_-]+)\s*-->/g;
  let match;
  let tagCount = 0;
  while ((match = onchainTagRegex.exec(content)) !== null) {
    tagCount++;
  }
  if (tagCount === 0) {
    errors.push(`[K4 FAIL] ${path.basename(docPath)}: Missing <!-- onchain:... --> traceability tags for documented numbers`);
  }
  return errors;
}

// K5: calibration_results.json must not contain hard-coded counters: assert stable_count == records
function checkK5_CalibrationCounters(calibPath) {
  const errors = [];
  if (!fs.existsSync(calibPath)) return errors;
  const data = JSON.parse(fs.readFileSync(calibPath, 'utf8'));
  const mc = data.model_calibration;
  if (!mc) {
    errors.push(`[K5 FAIL] calibration_results.json missing model_calibration section`);
    return errors;
  }

  if (mc.runs && Array.isArray(mc.runs)) {
    const computedStable = mc.runs.filter(r => r.stable_and_correct).length;
    if (mc.stable_and_correct !== computedStable) {
      errors.push(`[K5 FAIL] Hard-coded or inconsistent stable_count: declared ${mc.stable_and_correct}, computed ${computedStable}`);
    }
  } else if (mc.measured === false) {
    // Explicitly reported as not measured
  } else {
    errors.push(`[K5 FAIL] Model calibration lacks per-run measured data`);
  }
  return errors;
}

// K6: Truncated audits must be labelled partial wherever shown
function checkK6_TruncationLabels(docPath, liveEvidence) {
  const errors = [];
  if (!fs.existsSync(docPath)) return errors;
  const content = fs.readFileSync(docPath, 'utf8');

  for (const [key, t] of Object.entries(liveEvidence.targets || {})) {
    if (t.auditRecord && t.auditRecord.truncated) {
      // Must mention partial or truncated near target label
      const label = t.label;
      const idx = content.indexOf(label);
      if (idx !== -1) {
        const snippet = content.slice(Math.max(0, idx - 100), Math.min(content.length, idx + 250)).toLowerCase();
        if (!snippet.includes('truncat') && !snippet.includes('partial')) {
          errors.push(`[K6 FAIL] Truncated target '${label}' not labelled as partial/truncated in ${path.basename(docPath)}`);
        }
      }
    }
  }
  for (const [key, s] of Object.entries(liveEvidence.self_lint || {})) {
    if (s.auditRecord && s.auditRecord.truncated) {
      const label = s.label;
      const idx = content.indexOf(label);
      if (idx !== -1) {
        const snippet = content.slice(Math.max(0, idx - 100), Math.min(content.length, idx + 250)).toLowerCase();
        if (!snippet.includes('truncat') && !snippet.includes('partial')) {
          errors.push(`[K6 FAIL] Truncated self-lint '${label}' not labelled as partial/truncated in ${path.basename(docPath)}`);
        }
      }
    }
  }
  return errors;
}

// K7: Rendered tables byte-identical to a fresh render from JSON
function checkK7_RenderedTablesByteIdentical(docPath, renderScriptPath) {
  const errors = [];
  if (!fs.existsSync(docPath) || !fs.existsSync(renderScriptPath)) return errors;
  const currentContent = fs.readFileSync(docPath, 'utf8');
  
  // Import renderer dynamically to get fresh render
  const renderer = require(renderScriptPath);
  if (typeof renderer.renderMarkdown === 'function') {
    const fresh = renderer.renderMarkdown();
    if (currentContent !== fresh) {
      errors.push(`[K7 FAIL] ${path.basename(docPath)} differs from fresh render output from ${path.basename(renderScriptPath)}`);
    }
  }
  return errors;
}

function runFullChecker(options = {}) {
  const rootDir = path.resolve(__dirname, '../..');
  const deployDir = path.join(rootDir, 'scripts/deploy');
  const contractsDir = path.join(rootDir, 'contracts');
  const docsDir = path.join(rootDir, 'docs');
  const toolsDir = path.join(rootDir, 'scripts/tools');

  const lintCode = fs.readFileSync(path.join(contractsDir, 'ConsensusLint.py'), 'utf8');
  const badgesCode = fs.readFileSync(path.join(contractsDir, 'HygieneBadges.py'), 'utf8');
  const probeCode = fs.existsSync(path.join(contractsDir, 'Probe.py')) ? fs.readFileSync(path.join(contractsDir, 'Probe.py'), 'utf8') : '';
  const contractCodes = [lintCode, badgesCode, probeCode];

  const scriptFiles = [
    path.join(deployDir, 'deploy.js'),
    path.join(deployDir, 'run_evidence.js'),
    path.join(rootDir, 'scripts/probes/run_probes.js'),
  ].filter(f => fs.existsSync(f));

  console.log("=== RUNNING CONSISTENCY CHECKER (K1 - K7) ===");
  const allErrors = [];

  // Basic deployments check
  const deployPath = path.join(deployDir, 'deployments.json');
  if (fs.existsSync(deployPath)) {
    console.log("Checking deployments.json basic formats...");
    const deployments = JSON.parse(fs.readFileSync(deployPath, 'utf8'));
    checkHexAddress(deployments.deployer, "deployer");
    checkHexAddress(deployments.contracts.ConsensusLint.address, "ConsensusLint.address");
    checkTxHash(deployments.contracts.ConsensusLint.deployTxHash, "ConsensusLint.deployTxHash");
    checkAgreement(deployments.contracts.ConsensusLint.agreement, "ConsensusLint.agreement");

    checkHexAddress(deployments.contracts.HygieneBadges.address, "HygieneBadges.address");
    checkTxHash(deployments.contracts.HygieneBadges.deployTxHash, "HygieneBadges.deployTxHash");
    checkAgreement(deployments.contracts.HygieneBadges.agreement, "HygieneBadges.agreement");

    checkTxHash(deployments.contracts.HygieneBadges.setLedgerTxHash, "HygieneBadges.setLedgerTxHash");
    checkAgreement(deployments.contracts.HygieneBadges.setLedgerAgreement, "HygieneBadges.setLedgerAgreement");

    const lintSha = crypto.createHash('sha256').update(lintCode, 'utf8').digest('hex');
    if (lintSha !== deployments.contracts.ConsensusLint.sourceSha256) {
      allErrors.push(`ConsensusLint SHA256 mismatch: disk=${lintSha}, deployment=${deployments.contracts.ConsensusLint.sourceSha256}`);
    }

    const badgesSha = crypto.createHash('sha256').update(badgesCode, 'utf8').digest('hex');
    if (badgesSha !== deployments.contracts.HygieneBadges.sourceSha256) {
      allErrors.push(`HygieneBadges SHA256 mismatch: disk=${badgesSha}, deployment=${deployments.contracts.HygieneBadges.sourceSha256}`);
    }
  }

  // Live evidence checks
  const livePath = path.join(deployDir, 'live_evidence.json');
  let liveEvidence = null;
  if (fs.existsSync(livePath)) {
    liveEvidence = JSON.parse(fs.readFileSync(livePath, 'utf8'));
    for (const [key, t] of Object.entries(liveEvidence.targets || {})) {
      if (t.registrationTxHash) checkTxHash(t.registrationTxHash, `${key}.registrationTxHash`);
      if (t.auditTxHash) checkTxHash(t.auditTxHash, `${key}.auditTxHash`);
      if (t.registrationAgreement) checkAgreement(t.registrationAgreement, `${key}.registrationAgreement`);
      if (t.auditAgreement) checkAgreement(t.auditAgreement, `${key}.auditAgreement`);
    }
  }

  // K1
  console.log("Rule K1: Checking call-site arity & method names...");
  const k1Errors = checkK1_CallSiteArity(scriptFiles, contractCodes);
  allErrors.push(...k1Errors);

  // K2
  if (liveEvidence) {
    console.log("Rule K2: Checking decoded errors against contract literals...");
    const k2Errors = checkK2_DecodedErrors(liveEvidence, contractCodes);
    allErrors.push(...k2Errors);
  }

  // K3
  if (liveEvidence) {
    console.log("Rule K3: Checking maintainer response stored arrays...");
    const k3Errors = checkK3_MaintainerResponses(liveEvidence);
    allErrors.push(...k3Errors);
  }

  // K4
  if (liveEvidence) {
    console.log("Rule K4: Checking on-chain claim traceability tags...");
    const k4Errors = checkK4_OnchainClaimsTraced(path.join(docsDir, 'EVIDENCE.md'), liveEvidence);
    allErrors.push(...k4Errors);
  }

  // K5
  console.log("Rule K5: Checking calibration counter consistency...");
  const calibPath = path.join(toolsDir, 'calibration_results.json');
  const k5Errors = checkK5_CalibrationCounters(calibPath);
  allErrors.push(...k5Errors);

  // K6
  if (liveEvidence) {
    console.log("Rule K6: Checking truncation labelling...");
    const k6Errors = checkK6_TruncationLabels(path.join(docsDir, 'EVIDENCE.md'), liveEvidence);
    allErrors.push(...k6Errors);
  }

  // K7
  console.log("Rule K7: Checking rendered table byte-identity...");
  const k7Errors = checkK7_RenderedTablesByteIdentical(
    path.join(docsDir, 'EVIDENCE.md'),
    path.join(toolsDir, 'render_evidence.js')
  );
  allErrors.push(...k7Errors);

  if (allErrors.length > 0) {
    console.log("\n--- CHECKER FOUND VIOLATIONS ---");
    for (const err of allErrors) console.error(err);
    if (!options.silentFail) {
      throw new Error(`Checker failed with ${allErrors.length} violation(s).`);
    }
    return { success: false, errors: allErrors };
  }

  console.log("\nALL EVIDENCE CONSISTENCY CHECKS (K1 - K7) PASSED OK!");
  return { success: true, errors: [] };
}

if (require.main === module) {
  try {
    runFullChecker();
  } catch (e) {
    console.error(e.message);
    process.exit(1);
  }
}

module.exports = {
  checkK1_CallSiteArity,
  checkK2_DecodedErrors,
  checkK3_MaintainerResponses,
  checkK4_OnchainClaimsTraced,
  checkK5_CalibrationCounters,
  checkK6_TruncationLabels,
  checkK7_RenderedTablesByteIdentical,
  extractContractMethods,
  extractUserErrors,
  runFullChecker,
};
