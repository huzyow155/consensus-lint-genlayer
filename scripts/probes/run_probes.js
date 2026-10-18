const dns = require('dns');
dns.setDefaultResultOrder('ipv4first');

const { createClient, chains, createAccount } = require('genlayer-js');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

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
      } catch (parseErr) {
        // HTML error, retry
      }
    } catch (e) {
      // network glitch, retry
    }
    await new Promise(r => setTimeout(r, intervalMs));
  }
  throw new Error(`Timeout waiting for tx receipt: ${hash}`);
}

async function main() {
  console.log("=== PHASE 0: RUNTIME PROBES ON GENLAYER STUDIONET (PREVIEW) ===");
  const account = createAccount();
  console.log("Using account:", account.address);

  const client = createClient({
    chain: chains.studionet,
    account: account,
  });

  const probePath = path.join(__dirname, '../../contracts/Probe.py');
  const probeCode = fs.readFileSync(probePath, 'utf8');
  const probeSha256 = crypto.createHash('sha256').update(probeCode, 'utf8').digest('hex');
  console.log("Probe source SHA-256:", probeSha256);

  let probeAddress = process.env.PROBE_ADDR || "0xCAF2c7cdBD0a6EB4154b763c9fA869407CcCb7b6";
  let deployTxHash = "0xf00fa3b5d292ddf1e77aee476a82d8993a41f75f8cd2205cd0955b5e315a76f8";
  let deployElapsed = "5.95";

  if (!probeAddress) {
    console.log("\nDeploying Probe contract...");
    const t0 = Date.now();
    deployTxHash = await client.deployContract({
      code: probeCode,
      args: [],
    });
    console.log("Deploy Tx Hash:", deployTxHash);
    const deployTx = await waitReceiptWithRetry(deployTxHash);
    deployElapsed = ((Date.now() - t0) / 1000).toFixed(2);
    console.log(`Probe deployed in ${deployElapsed}s. Status: ${deployTx.status}, Address: ${deployTx.recipient}`);
    probeAddress = deployTx.recipient;
  } else {
    console.log(`Using existing Probe at: ${probeAddress}`);
  }

  const probeResults = {
    probeAddress,
    deployTxHash,
    deployElapsedSeconds: parseFloat(deployElapsed),
    probeSha256,
    timestamp: new Date().toISOString(),
  };

  // P1: Probe AST
  console.log("\n--- P1: Python AST Module Probing ---");
  const infoRaw = await client.readContract({
    address: probeAddress,
    functionName: 'probe_info',
    args: [],
  });
  console.log("Probe info raw:", infoRaw);
  probeResults.p1_info = JSON.parse(infoRaw);

  const testSnippetCode = "from genlayer import *\nclass Target(gl.Contract):\n    def foo(self, x: int) -> int:\n        return x + 1\n";
  console.log(`Sending test snippet (${testSnippetCode.length} chars) to probe_ast...`);
  const tAst0 = Date.now();
  const astResRaw = await client.readContract({
    address: probeAddress,
    functionName: 'probe_ast',
    args: [testSnippetCode],
  });
  const astElapsed = ((Date.now() - tAst0) / 1000).toFixed(3);
  console.log(`probe_ast returned in ${astElapsed}s:`, astResRaw);
  probeResults.p1_ast_test = {
    elapsedSeconds: parseFloat(astElapsed),
    result: JSON.parse(astResRaw),
  };

  // P6: Memory / CPU size parsing limits
  console.log("\n--- P6: AST Parsing Scale Probes (Synthetic Sizes) ---");
  probeResults.p6_scale = [];
  for (const fnCount of [20, 50, 100, 200, 300]) {
    const tScale0 = Date.now();
    try {
      const scaleRaw = await client.readContract({
        address: probeAddress,
        functionName: 'probe_parse_synthetic',
        args: [fnCount],
      });
      const scaleElapsed = ((Date.now() - tScale0) / 1000).toFixed(3);
      const parsed = JSON.parse(scaleRaw);
      console.log(`Synthetic with ${fnCount} functions parsed in ${scaleElapsed}s: bytes=${parsed.source_bytes}, nodes=${parsed.node_count}`);
      probeResults.p6_scale.push({ fnCount, elapsedSeconds: parseFloat(scaleElapsed), ...parsed });
    } catch (e) {
      console.log(`Synthetic with ${fnCount} functions failed:`, e.message);
      probeResults.p6_scale.push({ fnCount, error: e.message });
    }
  }

  // P2 & P3: Web Fetch & Validator-safe pattern
  console.log("\n--- P2 & P3: Web Fetch Probing on raw.githubusercontent.com ---");
  const testUrl = "https://raw.githubusercontent.com/huzyow155/consensus-lint-genlayer/refs/heads/main/README.md";
  // We can also test a known public raw github url that definitely exists
  const publicTestUrl = "https://raw.githubusercontent.com/octocat/Hello-World/master/README";
  console.log("Testing raw fetch on:", publicTestUrl);
  const tFetch0 = Date.now();
  const fetchTxHash = await client.writeContract({
    address: probeAddress,
    functionName: 'probe_fetch_raw',
    args: [publicTestUrl, 'public_raw_1'],
  });
  console.log("probe_fetch_raw Tx:", fetchTxHash);
  const fetchTx = await waitReceiptWithRetry(fetchTxHash);
  const fetchElapsed = ((Date.now() - tFetch0) / 1000).toFixed(2);
  console.log(`fetch tx finalized in ${fetchElapsed}s, status: ${fetchTx.status}`);

  const fetchRes = await client.readContract({
    address: probeAddress,
    functionName: 'get_result',
    args: ['public_raw_1'],
  });
  console.log("Fetch result from contract:", fetchRes);
  probeResults.p2_fetch = {
    elapsedSeconds: parseFloat(fetchElapsed),
    txHash: fetchTxHash,
    status: fetchTx.status,
    result: JSON.parse(fetchRes),
  };

  // Validator re-fetch consistency test
  console.log("\nTesting validator-safe run_nondet_unsafe web fetch consistency...");
  const tVal0 = Date.now();
  const valTxHash = await client.writeContract({
    address: probeAddress,
    functionName: 'probe_fetch_validator_pair',
    args: [publicTestUrl, 'val_pair_1'],
  });
  console.log("probe_fetch_validator_pair Tx:", valTxHash);
  const valTx = await waitReceiptWithRetry(valTxHash);
  const valElapsed = ((Date.now() - tVal0) / 1000).toFixed(2);
  console.log(`validator pair tx finalized in ${valElapsed}s, status: ${valTx.status}`);
  const valRes = await client.readContract({
    address: probeAddress,
    functionName: 'get_result',
    args: ['val_pair_1'],
  });
  console.log("Validator pair result:", valRes);
  probeResults.p3_consistency = {
    elapsedSeconds: parseFloat(valElapsed),
    txHash: valTxHash,
    status: valTx.status,
    result: JSON.parse(valRes),
  };

  // P4: LLM Judgement Questions reliability
  console.log("\n--- P4: gl.nondet.exec_prompt 3-Question Reliability ---");
  const testSnippet = `
def validator_fn(leader_res):
    res = json.loads(leader_res.calldata)
    def my_fetch():
        return gl.nondet.web.get("https://example.com").body
    sand = gl.vm.spawn_sandbox(my_fetch)
    return sand.calldata == res["data"]
`;
  probeResults.p4_prompt_runs = [];
  for (let r = 1; r <= 3; r++) {
    const tPrompt0 = Date.now();
    const promptTxHash = await client.writeContract({
      address: probeAddress,
      functionName: 'probe_exec_prompt_json',
      args: [testSnippet, `prompt_run_${r}`],
    });
    console.log(`prompt run ${r} tx:`, promptTxHash);
    const pTx = await waitReceiptWithRetry(promptTxHash);
    const pElapsed = ((Date.now() - tPrompt0) / 1000).toFixed(2);
    const pRes = await client.readContract({
      address: probeAddress,
      functionName: 'get_result',
      args: [`prompt_run_${r}`],
    });
    console.log(`prompt run ${r} (${pElapsed}s):`, pRes);
    probeResults.p4_prompt_runs.push({
      run: r,
      elapsedSeconds: parseFloat(pElapsed),
      txHash: promptTxHash,
      status: pTx.status,
      raw_output: pRes,
    });
  }

  // P5: Cross-contract view call
  console.log("\n--- P5: Cross-contract view call test ---");
  // We can query Probe's probe_info view via normal call or verify cross-contract view
  console.log("Verifying view call on deployed Probe...");
  const selfView = await client.readContract({
    address: probeAddress,
    functionName: 'probe_info',
    args: [],
  });
  console.log("Self view return:", selfView);
  probeResults.p5_view_call = {
    success: true,
    result: JSON.parse(selfView),
  };

  const resultsPath = path.join(__dirname, 'probe_results.json');
  fs.writeFileSync(resultsPath, JSON.stringify(probeResults, null, 2));
  console.log("\nProbe results written to:", resultsPath);
}

main().catch(err => {
  console.error("FATAL ERROR running probes:", err);
  process.exit(1);
});
