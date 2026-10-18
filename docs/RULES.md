# ConsensusLint Rule Catalogue (CL01 - CL18)

This document provides the complete specification of the 18 consensus-hygiene rules enforced by **ConsensusLint** on **GenLayer Studionet (Preview)**.

> [!NOTE]
> Rules are categorized by severity (**CRITICAL**: 20 pts, **MAJOR**: 8 pts, **MINOR**: 3 pts, **INFO**: 0 pts) and detection method (**STRUCTURAL**: deterministic AST check, **HEURISTIC**: AST pattern matching, or **MODEL**: bounded LLM quote verification).

---

## Summary Table

| Rule ID | Severity | Method | Weight | Max Cap | Name |
|---|---|---|---|---|---|
| `CL01` | MINOR | STRUCTURAL | 3 | 3 | Missing or invalid version header |
| `CL02` | MAJOR | STRUCTURAL | 8 | 2 | Missing or invalid py-genlayer dependency pin |
| `CL03` | MINOR | STRUCTURAL | 3 | 3 | Non-ASCII characters in contract source |
| `CL04` | INFO | STRUCTURAL | 0 | 0 | Not a GenLayer contract class |
| `CL05` | MAJOR | STRUCTURAL | 8 | 2 | TreeMap assignment in __init__ |
| `CL06` | MINOR | HEURISTIC | 3 | 3 | Unbounded list load-append-store pattern |
| `CL07` | MAJOR | HEURISTIC | 8 | 2 | strict_eq used on dynamic payload or free-text |
| `CL08` | MAJOR | STRUCTURAL | 8 | 2 | Non-deterministic call outside consensus wrapper |
| `CL09` | CRITICAL | STRUCTURAL | 20 | 1 | Validator does not recompute verdict |
| `CL10` | MAJOR | STRUCTURAL | 8 | 2 | Validator accesses calldata without Return check |
| `CL11` | MAJOR | STRUCTURAL | 8 | 2 | Validator waves through failures in except handler |
| `CL12` | MAJOR | HEURISTIC | 8 | 2 | Silent default fallback on model parse failure |
| `CL13` | MAJOR | STRUCTURAL | 8 | 2 | Wall-clock time call used instead of chain clock |
| `CL14` | MINOR | STRUCTURAL | 3 | 3 | Generic exception or assert used in public methods |
| `CL15` | MAJOR | HEURISTIC | 8 | 2 | URL validation by substring or prefix check |
| `CL16` | MINOR | HEURISTIC | 3 | 3 | Unbounded string parameter in public write method |
| `CL17` | MINOR | HEURISTIC | 3 | 3 | Unpaginated view method iterating collection |
| `CL18` | INFO | HEURISTIC | 0 | 0 | Public parameter in prompt without visible sanitization |

---

## Detailed Rule Specifications

### CL01: Missing or invalid version header
- **Severity**: MINOR (3 points)
- **Method**: STRUCTURAL
- **Why It Matters**: GenLayer runtime relies on version pragma comments at the very beginning of the source (e.g. `# v0.2.16`) to select the appropriate GenVM runner.
- **Bad Example**:
  ```python
  from genlayer import *
  class MyContract(gl.Contract):
      pass
  ```
- **Good Example**:
  ```python
  # v0.2.16
  # { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
  from genlayer import *
  ```

---

### CL02: Missing or invalid py-genlayer dependency pin
- **Severity**: MAJOR (8 points)
- **Method**: STRUCTURAL
- **Why It Matters**: Unpinned SDK dependencies cause consensus divergence if different validator nodes resolve different SDK minor versions.
- **Bad Example**:
  ```python
  # v0.2.16
  # Depends: py-genlayer
  ```
- **Good Example**:
  ```python
  # v0.2.16
  # { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
  ```

---

### CL03: Non-ASCII characters in contract source
- **Severity**: MINOR (3 points)
- **Method**: STRUCTURAL
- **Why It Matters**: Non-ASCII characters in docstrings or comments can lead to character encoding mismatches (UTF-8 vs CP-1252) across heterogenous validator systems.
- **Bad Example**:
  ```python
  # v0.2.16
  # { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
  # Author: Ren\u00e9 Descartes
  ```
- **Good Example**:
  ```python
  # v0.2.16
  # { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
  # Author: Rene Descartes (ASCII)
  ```

---

### CL04: Not a GenLayer contract class
- **Severity**: INFO (0 points, mode set to `NOT_A_CONTRACT`)
- **Method**: STRUCTURAL
- **Why It Matters**: Target file must define a class inheriting from `gl.Contract`. If absent, file is classified as a script or library and assigned Grade F.
- **Bad Example**:
  ```python
  def helper():
      return 42
  ```
- **Good Example**:
  ```python
  from genlayer import *
  class Vault(gl.Contract):
      pass
  ```

---

### CL05: TreeMap assignment in __init__
- **Severity**: MAJOR (8 points)
- **Method**: STRUCTURAL
- **Why It Matters**: GenVM stores TreeMap structures in persistent database slots. Assigning a dictionary or initializing TreeMap instances in `__init__` can cause state corruption. Persistent collections must use lazy initialization via `_ensure_meta_init()`.
- **Bad Example**:
  ```python
  class Registry(gl.Contract):
      records: TreeMap[str, str]
      def __init__(self):
          self.records = {}
  ```
- **Good Example**:
  ```python
  class Registry(gl.Contract):
      records: TreeMap[str, str]
      def __init__(self):
          pass  # Lazy init on first write
  ```

---

### CL06: Unbounded list load-append-store pattern
- **Severity**: MINOR (3 points)
- **Method**: HEURISTIC
- **Why It Matters**: Deserializing a JSON list, appending an item, and serializing it back in a public write method leads to O(n) compute and storage growth that eventually exceeds transaction gas limits.
- **Bad Example**:
  ```python
  @gl.public.write
  def add_entry(self, val: str):
      items = json.loads(self.meta.get("list", "[]"))
      items.append(val)
      self.meta["list"] = json.dumps(items)
  ```
- **Good Example**:
  ```python
  @gl.public.write
  def add_entry(self, val: str):
      idx = int(self.meta.get("total", "0"))
      self.meta[f"item:{idx}"] = val
      self.meta["total"] = str(idx + 1)
  ```

---

### CL07: strict_eq used on dynamic payload or free-text
- **Severity**: MAJOR (8 points)
- **Method**: HEURISTIC
- **Why It Matters**: `gl.eq_principle.strict_eq` requires identical byte-for-byte strings across validators. When evaluated on LLM output or dynamic JSON, minor formatting differences cause `NO_MAJORITY` consensus failures.
- **Bad Example**:
  ```python
  gl.eq_principle.strict_eq(lambda: f"Summary: {gl.nondet.exec_prompt(p)}")
  ```
- **Good Example**:
  ```python
  # Custom leader/validator pattern with closed-enumeration verdict
  res = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
  ```

---

### CL08: Non-deterministic call outside consensus wrapper
- **Severity**: MAJOR (8 points)
- **Method**: STRUCTURAL
- **Why It Matters**: Non-deterministic operations (`gl.nondet.web.get`, `gl.nondet.exec_prompt`) executed directly in contract state methods diverge across validator nodes.
- **Bad Example**:
  ```python
  @gl.public.write
  def update(self):
      data = gl.nondet.web.get("https://example.com").body
      self.meta["data"] = str(data)
  ```
- **Good Example**:
  ```python
  @gl.public.write
  def update(self):
      def fetch_leader():
          return gl.vm.spawn_sandbox(lambda: gl.nondet.web.get("https://example.com").body)
      res = gl.vm.run_nondet_unsafe(fetch_leader, validator_checker)
  ```

---

### CL09: Validator does not recompute verdict
- **Severity**: CRITICAL (20 points)
- **Method**: STRUCTURAL
- **Why It Matters**: If a validator unconditionally returns `True` or performs no independent computation, malicious leaders can forge state transitions with zero verification.
- **Bad Example**:
  ```python
  def validator_fn(leader_res):
      return True  # Zero verification!
  ```
- **Good Example**:
  ```python
  def validator_fn(leader_res):
      sand = gl.vm.spawn_sandbox(independent_fetch)
      return sand.calldata == json.loads(leader_res.calldata)["hash"]
  ```

---

### CL10: Validator accesses calldata without Return check
- **Severity**: MAJOR (8 points)
- **Method**: STRUCTURAL
- **Why It Matters**: Leader execution can encounter runtime errors or rollbacks. Accessing `leader_res.calldata` without checking `isinstance(leader_res, gl.vm.Return)` causes unhandled exceptions in validators.
- **Bad Example**:
  ```python
  def validator_fn(leader_res):
      data = leader_res.calldata
  ```
- **Good Example**:
  ```python
  def validator_fn(leader_res):
      if not isinstance(leader_res, gl.vm.Return):
          return False
      data = leader_res.calldata
  ```

---

### CL11: Validator waves through failures in except handler
- **Severity**: MAJOR (8 points)
- **Method**: STRUCTURAL
- **Why It Matters**: Catching exceptions in validator code and returning `True` causes validators to accept invalid transactions whenever an error occurs.
- **Bad Example**:
  ```python
  def validator_fn(leader_res):
      try:
          verify(leader_res)
      except Exception:
          return True  # Waved through!
  ```
- **Good Example**:
  ```python
  def validator_fn(leader_res):
      try:
          return verify(leader_res)
      except Exception:
          return False
  ```

---

### CL12: Silent default fallback on model parse failure
- **Severity**: MAJOR (8 points)
- **Method**: HEURISTIC
- **Why It Matters**: Mapping a malformed model output to a silent default value masks prompt injection or invalid reasoning and records erroneous consensus state.
- **Bad Example**:
  ```python
  try:
      score = json.loads(prompt_out)["score"]
  except Exception:
      score = 0  # Silent default fallback
  ```
- **Good Example**:
  ```python
  try:
      score = json.loads(prompt_out)["score"]
  except Exception:
      raise gl.vm.UserError("model output malformed")
  ```

---

### CL13: Wall-clock time call used instead of chain clock
- **Severity**: MAJOR (8 points)
- **Method**: STRUCTURAL
- **Why It Matters**: Using `datetime.now()` or `time.time()` causes transactions to produce different timestamps on each validator node, breaking consensus.
- **Bad Example**:
  ```python
  now = datetime.now()
  ```
- **Good Example**:
  ```python
  now = gl.message_raw["datetime"]
  ```

---

### CL14: Generic exception or assert used in public methods
- **Severity**: MINOR (3 points)
- **Method**: STRUCTURAL
- **Why It Matters**: Standard `assert` statements or generic `raise Exception` can lead to non-descriptive VM crashes. Public validation must use `raise gl.vm.UserError("<exact message>")`.
- **Bad Example**:
  ```python
  assert amount > 0, "Amount must be positive"
  ```
- **Good Example**:
  ```python
  if amount <= 0:
      raise gl.vm.UserError("amount must be positive")
  ```

---

### CL15: URL validation by substring or prefix check
- **Severity**: MAJOR (8 points)
- **Method**: HEURISTIC
- **Why It Matters**: Checking URLs using `url.startswith("https://github.com")` or `"github.com" in url` allows attackers to bypass security using domains like `https://github.com.attacker.com`.
- **Bad Example**:
  ```python
  if "raw.githubusercontent.com" not in url:
      raise gl.vm.UserError("invalid url")
  ```
- **Good Example**:
  ```python
  parsed = urllib.parse.urlsplit(url)
  if parsed.hostname != "raw.githubusercontent.com":
      raise gl.vm.UserError("invalid source host")
  ```

---

### CL16: Unbounded string parameter in public write method
- **Severity**: MINOR (3 points)
- **Method**: HEURISTIC
- **Why It Matters**: Public string arguments without explicit `len(param)` boundaries permit unbounded calldata injection that exhausts validator memory or gas limits.
- **Bad Example**:
  ```python
  @gl.public.write
  def set_description(self, desc: str):
      self.meta["desc"] = desc
  ```
- **Good Example**:
  ```python
  @gl.public.write
  def set_description(self, desc: str):
      if not isinstance(desc, str) or len(desc) > 280:
          raise gl.vm.UserError("invalid description length")
      self.meta["desc"] = desc
  ```

---

### CL17: Unpaginated view method iterating collection
- **Severity**: MINOR (3 points)
- **Method**: HEURISTIC
- **Why It Matters**: Public view functions iterating entire state collections without pagination parameters (`offset`, `limit`) fail once collections exceed RPC response buffers.
- **Bad Example**:
  ```python
  @gl.public.view
  def list_all(self) -> str:
      return json.dumps([self.meta[f"tid:{i}"] for i in range(self.total)])
  ```
- **Good Example**:
  ```python
  @gl.public.view
  def list_ids(self, offset: int, limit: int) -> str:
      lim = min(50, max(1, int(limit)))
      off = max(0, int(offset))
      return json.dumps([self.meta[f"tid:{i}"] for i in range(off, off + lim)])
  ```

---

### CL18: Public parameter in prompt without visible sanitization
- **Severity**: INFO (0 points)
- **Method**: HEURISTIC
- **Why It Matters**: Inserting user-supplied strings directly into model prompt templates risks prompt injection. Prompts should sanitize or quote user input.
- **Bad Example**:
  ```python
  prompt = f"Analyze this user query: {user_input}"
  ```
- **Good Example**:
  ```python
  safe_input = json.dumps(user_input.strip()[:100])
  prompt = f"Analyze the following query snippet:\n{safe_input}"
  ```
