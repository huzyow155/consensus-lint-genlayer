# scripts/tools/generate_fixtures.py
import os

RULES = [
    "CL01", "CL02", "CL03", "CL04", "CL05", "CL06",
    "CL07", "CL08", "CL09", "CL10", "CL11", "CL12",
    "CL13", "CL14", "CL15", "CL16", "CL17", "CL18"
]

HEADER = '# v0.2.16\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\nfrom genlayer import *\n'

FIXTURES = {
    "CL01": {
        "pass_1.py": '# v0.2.16\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\nfrom genlayer import *\nclass Good(gl.Contract):\n    pass\n',
        "pass_2.py": '# v0.2.0\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\nfrom genlayer import *\nclass AlsoGood(gl.Contract):\n    pass\n',
        "fail_1.py": '# v0.1.9\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\nfrom genlayer import *\nclass BadVersion(gl.Contract):\n    pass\n',
        "fail_2.py": '# Missing version header entirely\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\nfrom genlayer import *\nclass NoVersion(gl.Contract):\n    pass\n',
    },
    "CL02": {
        "pass_1.py": '# v0.2.16\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\nfrom genlayer import *\nclass DepOk(gl.Contract):\n    pass\n',
        "pass_2.py": '# v0.2.16\n# { "Depends": "py-genlayer:abcdef0123456789abcdef0123456789abcdef0123456789abcdef01" }\nfrom genlayer import *\nclass DepAlsoOk(gl.Contract):\n    pass\n',
        "fail_1.py": '# v0.2.16\n# No dependency header\nfrom genlayer import *\nclass DepMissing(gl.Contract):\n    pass\n',
        "fail_2.py": '# v0.2.16\n# { "Depends": "py-genlayer:too_short_hash" }\nfrom genlayer import *\nclass DepShort(gl.Contract):\n    pass\n',
    },
    "CL03": {
        "pass_1.py": HEADER + 'class AsciiOnly(gl.Contract):\n    # Pure ascii comments and symbols\n    pass\n',
        "pass_2.py": HEADER + 'class AsciiSimple(gl.Contract):\n    val: str\n    def __init__(self):\n        self.val = "safe_ascii"\n',
        "fail_1.py": HEADER + 'class UnicodeChar(gl.Contract):\n    # Non-ascii: \u2022 bullet point\n    pass\n',
        "fail_2.py": HEADER + 'class UnicodeQuote(gl.Contract):\n    # Non-ascii: \u201chello\u201d\n    pass\n',
    },
    "CL04": {
        "pass_1.py": HEADER + 'class ValidContract(gl.Contract):\n    pass\n',
        "pass_2.py": HEADER + 'from genlayer import Contract\nclass AnotherValid(Contract):\n    pass\n',
        "fail_1.py": '# v0.2.16\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\ndef helper_func(x: int) -> int:\n    return x + 1\n',
        "fail_2.py": '# v0.2.16\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\nclass RegularPythonClass:\n    def __init__(self):\n        self.a = 1\n',
    },
    "CL05": {
        "pass_1.py": HEADER + 'class LazyInit(gl.Contract):\n    records: TreeMap[str, str]\n    def __init__(self):\n        pass\n    def _ensure(self):\n        if "k" not in self.records: self.records["k"] = "v"\n',
        "pass_2.py": HEADER + 'class NoTreeMap(gl.Contract):\n    owner: str\n    def __init__(self):\n        self.owner = "0x123"\n',
        "fail_1.py": HEADER + 'class DirectMapAssign(gl.Contract):\n    store: TreeMap[str, str]\n    def __init__(self):\n        self.store["key"] = "val"\n',
        "fail_2.py": HEADER + 'class NewTreeMapAssign(gl.Contract):\n    store: TreeMap[str, str]\n    def __init__(self):\n        self.store = TreeMap()\n',
    },
    "CL06": {
        "pass_1.py": HEADER + 'import json\nclass BoundedList(gl.Contract):\n    map_store: TreeMap[str, str]\n    @gl.public.write\n    def append_capped(self, item: str) -> None:\n        raw = self.map_store.get("k", "[]")\n        lst = json.loads(raw)\n        if len(lst) >= 50: raise gl.vm.UserError("limit")\n        lst.append(item)\n        self.map_store["k"] = json.dumps(lst)\n',
        "pass_2.py": HEADER + 'class NoAppend(gl.Contract):\n    map_store: TreeMap[str, str]\n    @gl.public.write\n    def set_val(self, v: str) -> None:\n        if len(v) < 50: self.map_store["k"] = v\n',
        "fail_1.py": HEADER + 'import json\nclass UnboundedRebuild(gl.Contract):\n    map_store: TreeMap[str, str]\n    @gl.public.write\n    def add_item(self, item: str) -> None:\n        raw = self.map_store.get("k", "[]")\n        lst = json.loads(raw)\n        lst.append(item)\n        self.map_store["k"] = json.dumps(lst)\n',
        "fail_2.py": HEADER + 'import json\nclass AnotherUnbounded(gl.Contract):\n    data: TreeMap[str, str]\n    @gl.public.write\n    def push(self, val: str) -> None:\n        cur = json.loads(self.data.get("list", "[]"))\n        cur.append(val)\n        self.data["list"] = json.dumps(cur)\n',
    },
    "CL07": {
        "pass_1.py": HEADER + 'class EnumStrictEq(gl.Contract):\n    @gl.public.write\n    def run_check(self) -> None:\n        def check_status() -> str:\n            return "PASS"\n        res = gl.eq_principle.strict_eq(check_status)\n',
        "pass_2.py": HEADER + 'class NoStrictEq(gl.Contract):\n    @gl.public.write\n    def write_val(self) -> None:\n        pass\n',
        "fail_1.py": HEADER + 'import json\nclass JsonDumpStrictEq(gl.Contract):\n    @gl.public.write\n    def run_bad_eq(self) -> None:\n        def leader_calc():\n            return json.dumps({"status": "ok", "count": 10})\n        res = gl.eq_principle.strict_eq(leader_calc)\n',
        "fail_2.py": HEADER + 'class PromptStrictEq(gl.Contract):\n    @gl.public.write\n    def run_prompt_eq(self) -> None:\n        res = gl.eq_principle.strict_eq(lambda: gl.nondet.exec_prompt("hello"))\n',
    },
    "CL08": {
        "pass_1.py": HEADER + 'class WrappedNondet(gl.Contract):\n    @gl.public.write\n    def do_fetch(self) -> None:\n        def my_fetch():\n            return gl.nondet.web.get("https://example.com").status\n        sand = gl.vm.spawn_sandbox(my_fetch)\n',
        "pass_2.py": HEADER + 'class WrappedRunNondet(gl.Contract):\n    @gl.public.write\n    def do_call(self) -> None:\n        def l_fn(): return "OK"\n        def v_fn(res): return True\n        gl.vm.run_nondet(l_fn, v_fn)\n',
        "fail_1.py": HEADER + 'class DirectNondet(gl.Contract):\n    @gl.public.write\n    def bad_direct_fetch(self) -> None:\n        res = gl.nondet.web.get("https://example.com")\n',
        "fail_2.py": HEADER + 'class DirectPrompt(gl.Contract):\n    @gl.public.view\n    def bad_direct_prompt(self) -> str:\n        return gl.nondet.exec_prompt("say hi")\n',
    },
    "CL09": {
        "pass_1.py": HEADER + 'class GoodRecompute(gl.Contract):\n    @gl.public.write\n    def do_eval(self) -> None:\n        def l_fn(): return gl.nondet.web.get("https://example.com").status\n        def v_fn(res):\n            if not hasattr(res, "calldata"): return False\n            sand = gl.vm.spawn_sandbox(lambda: gl.nondet.web.get("https://example.com").status)\n            return sand.calldata == res.calldata\n        gl.vm.run_nondet_unsafe(l_fn, v_fn)\n',
        "pass_2.py": HEADER + 'class AnotherRecompute(gl.Contract):\n    @gl.public.write\n    def do_audit(self) -> None:\n        def lead(): return "HASH"\n        def val(lead_res):\n            if not hasattr(lead_res, "calldata"): return False\n            s = gl.vm.spawn_sandbox(lambda: gl.nondet.exec_prompt("q"))\n            return s.calldata == lead_res.calldata\n        gl.vm.run_nondet_unsafe(lead, val)\n',
        "fail_1.py": HEADER + 'class NoRecomputeVal(gl.Contract):\n    @gl.public.write\n    def do_blind(self) -> None:\n        def lead(): return "DATA"\n        def val(lead_res):\n            if not hasattr(lead_res, "calldata"): return False\n            return lead_res.calldata != ""\n        gl.vm.run_nondet_unsafe(lead, val)\n',
        "fail_2.py": HEADER + 'class UnconditionalTrueVal(gl.Contract):\n    @gl.public.write\n    def do_trust(self) -> None:\n        def lead(): return "DATA"\n        def val(lead_res):\n            return True\n        gl.vm.run_nondet_unsafe(lead, val)\n',
    },
    "CL10": {
        "pass_1.py": HEADER + 'class CheckedReturn(gl.Contract):\n    @gl.public.write\n    def audit(self) -> None:\n        def l_fn(): return "OK"\n        def v_fn(r):\n            if not isinstance(r, gl.vm.Return): return False\n            sand = gl.vm.spawn_sandbox(lambda: "OK")\n            return sand.calldata == r.calldata\n        gl.vm.run_nondet_unsafe(l_fn, v_fn)\n',
        "pass_2.py": HEADER + 'class CheckedHasattr(gl.Contract):\n    @gl.public.write\n    def audit(self) -> None:\n        def l_fn(): return "OK"\n        def v_fn(r):\n            if not hasattr(r, "calldata"): return False\n            sand = gl.vm.spawn_sandbox(lambda: "OK")\n            return sand.calldata == r.calldata\n        gl.vm.run_nondet_unsafe(l_fn, v_fn)\n',
        "fail_1.py": HEADER + 'class UncheckedReturn(gl.Contract):\n    @gl.public.write\n    def audit(self) -> None:\n        def l_fn(): return "OK"\n        def v_fn(r):\n            sand = gl.vm.spawn_sandbox(lambda: "OK")\n            return sand.calldata == r.calldata\n        gl.vm.run_nondet_unsafe(l_fn, v_fn)\n',
        "fail_2.py": HEADER + 'class DirectCalldata(gl.Contract):\n    @gl.public.write\n    def audit(self) -> None:\n        def l_fn(): return "OK"\n        def v_fn(r):\n            data = r.calldata\n            sand = gl.vm.spawn_sandbox(lambda: "OK")\n            return sand.calldata == data\n        gl.vm.run_nondet_unsafe(l_fn, v_fn)\n',
    },
    "CL11": {
        "pass_1.py": HEADER + 'class SafeExcept(gl.Contract):\n    @gl.public.write\n    def audit(self) -> None:\n        def l_fn(): return "OK"\n        def v_fn(r):\n            if not hasattr(r, "calldata"): return False\n            try:\n                sand = gl.vm.spawn_sandbox(lambda: "OK")\n                return sand.calldata == r.calldata\n            except Exception:\n                return False\n        gl.vm.run_nondet_unsafe(l_fn, v_fn)\n',
        "pass_2.py": HEADER + 'class RaiseExcept(gl.Contract):\n    @gl.public.write\n    def audit(self) -> None:\n        def l_fn(): return "OK"\n        def v_fn(r):\n            if not hasattr(r, "calldata"): return False\n            sand = gl.vm.spawn_sandbox(lambda: "OK")\n            return sand.calldata == r.calldata\n        gl.vm.run_nondet_unsafe(l_fn, v_fn)\n',
        "fail_1.py": HEADER + 'class WaveThroughExcept(gl.Contract):\n    @gl.public.write\n    def audit(self) -> None:\n        def l_fn(): return "OK"\n        def v_fn(r):\n            if not hasattr(r, "calldata"): return False\n            try:\n                sand = gl.vm.spawn_sandbox(lambda: "OK")\n                return sand.calldata == r.calldata\n            except Exception:\n                return True\n        gl.vm.run_nondet_unsafe(l_fn, v_fn)\n',
        "fail_2.py": HEADER + 'class PassWaveThrough(gl.Contract):\n    @gl.public.write\n    def audit(self) -> None:\n        def l_fn(): return "OK"\n        def v_fn(r):\n            if not hasattr(r, "calldata"): return False\n            try:\n                sand = gl.vm.spawn_sandbox(lambda: "OK")\n            except Exception:\n                pass\n            return True\n        gl.vm.run_nondet_unsafe(l_fn, v_fn)\n',
    },
    "CL12": {
        "pass_1.py": HEADER + 'import json\nclass StrictModelParse(gl.Contract):\n    @gl.public.write\n    def parse_out(self, raw: str) -> None:\n        try:\n            res = json.loads(raw)\n        except Exception:\n            raise gl.vm.UserError("model output invalid")\n',
        "pass_2.py": HEADER + 'class NoCatchDefault(gl.Contract):\n    @gl.public.write\n    def run(self) -> None:\n        pass\n',
        "fail_1.py": HEADER + 'import json\nclass DefaultModelFallback(gl.Contract):\n    @gl.public.write\n    def parse_out(self, raw: str) -> None:\n        try:\n            res = json.loads(raw)\n        except Exception:\n            res = {"label": "DEFAULT"}\n',
        "fail_2.py": HEADER + 'import json\nclass AssignDefaultOnExcept(gl.Contract):\n    @gl.public.write\n    def parse_out(self, raw: str) -> None:\n        try:\n            res = json.loads(raw)\n        except Exception:\n            status = "FALLBACK"\n',
    },
    "CL13": {
        "pass_1.py": HEADER + 'class ChainClockOk(gl.Contract):\n    @gl.public.view\n    def get_time(self) -> str:\n        return str(gl.message_raw.get("datetime", ""))\n',
        "pass_2.py": HEADER + 'class NoTime(gl.Contract):\n    pass\n',
        "fail_1.py": HEADER + 'import datetime\nclass WallClockNow(gl.Contract):\n    @gl.public.view\n    def get_time(self) -> str:\n        return str(datetime.datetime.now())\n',
        "fail_2.py": HEADER + 'import time\nclass WallClockTime(gl.Contract):\n    @gl.public.view\n    def get_time(self) -> float:\n        return time.time()\n',
    },
    "CL14": {
        "pass_1.py": HEADER + 'class CleanErrors(gl.Contract):\n    @gl.public.write\n    def test(self, x: int) -> None:\n        if x <= 0:\n            raise gl.vm.UserError("x must be positive")\n',
        "pass_2.py": HEADER + 'class CleanView(gl.Contract):\n    @gl.public.view\n    def test(self, x: int) -> int:\n        if x == 0:\n            raise gl.vm.UserError("zero disallowed")\n        return x\n',
        "fail_1.py": HEADER + 'class AssertInPublic(gl.Contract):\n    @gl.public.write\n    def test(self, x: int) -> None:\n        assert x > 0, "x must be positive"\n',
        "fail_2.py": HEADER + 'class ValueErrorInPublic(gl.Contract):\n    @gl.public.write\n    def test(self, x: int) -> None:\n        if x <= 0:\n            raise ValueError("bad x")\n',
    },
    "CL15": {
        "pass_1.py": HEADER + 'import urllib.parse\nclass ParsedUrl(gl.Contract):\n    @gl.public.write\n    def check_url(self, u: str) -> None:\n        p = urllib.parse.urlsplit(u)\n        if p.hostname != "github.com":\n            raise gl.vm.UserError("host not allowed")\n',
        "pass_2.py": HEADER + 'from urllib.parse import urlparse\nclass ParsedUrlFrom(gl.Contract):\n    @gl.public.write\n    def check(self, u: str) -> None:\n        p = urlparse(u)\n        if p.scheme != "https":\n            raise gl.vm.UserError("https only")\n',
        "fail_1.py": HEADER + 'class SubstringUrlCheck(gl.Contract):\n    @gl.public.write\n    def check(self, u: str) -> None:\n        if not u.startswith("https://"): raise gl.vm.UserError("invalid url")\n',
        "fail_2.py": HEADER + 'class InUrlCheck(gl.Contract):\n    @gl.public.write\n    def check(self, u: str) -> None:\n        if "raw.githubusercontent.com" in u: pass\n',
    },
    "CL16": {
        "pass_1.py": HEADER + 'class BoundedParam(gl.Contract):\n    @gl.public.write\n    def set_label(self, label: str) -> None:\n        if len(label) < 3 or len(label) > 80:\n            raise gl.vm.UserError("invalid label length")\n',
        "pass_2.py": HEADER + 'class IntParam(gl.Contract):\n    @gl.public.write\n    def set_num(self, n: int) -> None:\n        pass\n',
        "fail_1.py": HEADER + 'class UnboundedParam(gl.Contract):\n    data: TreeMap[str, str]\n    @gl.public.write\n    def set_note(self, note: str) -> None:\n        self.data["note"] = note\n',
        "fail_2.py": HEADER + 'class AnotherUnbounded(gl.Contract):\n    @gl.public.write\n    def post(self, text: str) -> None:\n        pass\n',
    },
    "CL17": {
        "pass_1.py": HEADER + 'class PaginatedView(gl.Contract):\n    items: TreeMap[str, str]\n    @gl.public.view\n    def list_items(self, offset: int, limit: int) -> list[str]:\n        return [self.items[str(i)] for i in range(offset, offset + limit)]\n',
        "pass_2.py": HEADER + 'class SingleItemView(gl.Contract):\n    items: TreeMap[str, str]\n    @gl.public.view\n    def get_item(self, key: str) -> str:\n        return self.items.get(key, "")\n',
        "fail_1.py": HEADER + 'class UnpaginatedView(gl.Contract):\n    items: TreeMap[str, str]\n    @gl.public.view\n    def list_all(self) -> list[str]:\n        return [self.items[str(i)] for i in range(10)]\n',
        "fail_2.py": HEADER + 'class UnpaginatedLoop(gl.Contract):\n    store: TreeMap[str, str]\n    @gl.public.view\n    def get_everything(self) -> list[str]:\n        res = []\n        for k in self.store:\n            res.append(self.store[k])\n        return res\n',
    },
    "CL18": {
        "pass_1.py": HEADER + 'class SanitizedPrompt(gl.Contract):\n    @gl.public.write\n    def ask(self, query: str) -> None:\n        clean = query.replace("`", "")\n        sand = gl.vm.spawn_sandbox(lambda: gl.nondet.exec_prompt(f"Question: {clean}"))\n',
        "pass_2.py": HEADER + 'class StaticPrompt(gl.Contract):\n    @gl.public.write\n    def run(self) -> None:\n        sand = gl.vm.spawn_sandbox(lambda: gl.nondet.exec_prompt("Static instruction"))\n',
        "fail_1.py": HEADER + 'class UnsanitizedPrompt(gl.Contract):\n    @gl.public.write\n    def ask(self, query: str) -> None:\n        sand = gl.vm.spawn_sandbox(lambda: gl.nondet.exec_prompt(f"Question: {query}"))\n',
        "fail_2.py": HEADER + 'class FormatPrompt(gl.Contract):\n    @gl.public.write\n    def analyze(self, code_str: str) -> None:\n        p = f"Analyze: {code_str}"\n        sand = gl.vm.spawn_sandbox(lambda: gl.nondet.exec_prompt(p))\n',
    },
}

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../fixtures-local/rules"))
    for rule, files in FIXTURES.items():
        rdir = os.path.join(base_dir, rule)
        os.makedirs(rdir, exist_ok=True)
        for fname, content in files.items():
            fpath = os.path.join(rdir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
    print(f"Generated {len(FIXTURES)} rules with {sum(len(f) for f in FIXTURES.values())} fixtures in {base_dir}")

if __name__ == "__main__":
    main()
