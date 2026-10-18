# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import hashlib
import urllib.parse
from genlayer import *

try:
    import ast
    AST_IMPORT_OK = True
    AST_IMPORT_ERR = ""
except Exception as _e:
    ast = None
    AST_IMPORT_OK = False
    AST_IMPORT_ERR = str(_e)


class Probe(gl.Contract):
    results: TreeMap[str, str]

    def __init__(self):
        pass

    @gl.public.view
    def probe_info(self) -> str:
        return json.dumps({
            "status": "ok",
            "ast_available": AST_IMPORT_OK,
            "ast_error": AST_IMPORT_ERR,
        })

    @gl.public.view
    def probe_ast(self, code: str) -> str:
        if not AST_IMPORT_OK or ast is None:
            return json.dumps({
                "success": False,
                "error": f"ast module unavailable: {AST_IMPORT_ERR}",
            })
        try:
            tree = ast.parse(code)
            total_nodes = 0
            fn_defs = 0
            class_defs = 0
            sample_lines = []
            has_get_source_segment = hasattr(ast, "get_source_segment")

            for node in ast.walk(tree):
                total_nodes += 1
                if isinstance(node, ast.FunctionDef):
                    fn_defs += 1
                    seg = ""
                    if has_get_source_segment:
                        try:
                            seg = ast.get_source_segment(code, node) or ""
                        except Exception:
                            seg = ""
                    sample_lines.append({
                        "name": node.name,
                        "lineno": getattr(node, "lineno", None),
                        "end_lineno": getattr(node, "end_lineno", None),
                        "segment_len": len(seg),
                    })
                elif isinstance(node, ast.ClassDef):
                    class_defs += 1

            return json.dumps({
                "success": True,
                "total_nodes": total_nodes,
                "functions": fn_defs,
                "classes": class_defs,
                "sample_functions": sample_lines[:5],
                "has_get_source_segment": has_get_source_segment,
                "code_len": len(code),
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
            })

    @gl.public.view
    def probe_parse_synthetic(self, num_functions: int) -> str:
        if not AST_IMPORT_OK or ast is None:
            return json.dumps({"success": False, "error": "ast unavailable"})
        try:
            lines = ["# synthetic test contract", "from genlayer import *", "class Synthetic(gl.Contract):"]
            for i in range(num_functions):
                lines.append(f"    def func_{i}(self, x: int) -> int:")
                lines.append(f"        val = x + {i}")
                lines.append(f"        return val * 2")
            src = "\n".join(lines)
            tree = ast.parse(src)
            count = sum(1 for _ in ast.walk(tree))
            return json.dumps({
                "success": True,
                "functions_generated": num_functions,
                "source_bytes": len(src.encode("utf-8")),
                "node_count": count,
            })
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    @gl.public.write
    def probe_fetch_raw(self, url: str, test_key: str) -> None:
        def fetch_run() -> str:
            res = gl.nondet.web.get(url)
            status_code = int(res.status)
            body_bytes = res.body if isinstance(res.body, (bytes, bytearray)) else str(res.body).encode("utf-8")
            body_sha256 = hashlib.sha256(body_bytes).hexdigest()
            has_bom = body_bytes.startswith(b"\xef\xbb\xbf")
            has_crlf = b"\r\n" in body_bytes
            return json.dumps({
                "status": status_code,
                "length": len(body_bytes),
                "sha256": body_sha256,
                "has_bom": has_bom,
                "has_crlf": has_crlf,
                "preview": body_bytes[:100].decode("utf-8", errors="replace"),
            }, sort_keys=True)

        decision = gl.eq_principle.strict_eq(fetch_run)
        self.results[test_key] = decision

    @gl.public.write
    def probe_fetch_validator_pair(self, url: str, test_key: str) -> None:
        def leader_fn() -> str:
            res = gl.nondet.web.get(url)
            body_bytes = res.body if isinstance(res.body, (bytes, bytearray)) else str(res.body).encode("utf-8")
            body_sha256 = hashlib.sha256(body_bytes).hexdigest()
            return json.dumps({
                "status": int(res.status),
                "length": len(body_bytes),
                "sha256": body_sha256,
            }, sort_keys=True)

        def validator_fn(leader_res) -> bool:
            if not hasattr(leader_res, "calldata"):
                return False
            try:
                lead_data = json.loads(leader_res.calldata)
            except Exception:
                return False

            def val_fetch():
                r = gl.nondet.web.get(url)
                b = r.body if isinstance(r.body, (bytes, bytearray)) else str(r.body).encode("utf-8")
                return hashlib.sha256(b).hexdigest()

            sand = gl.vm.spawn_sandbox(val_fetch)
            if not isinstance(sand, gl.vm.Return):
                return False
            val_sha = sand.calldata
            return val_sha == lead_data.get("sha256")

        res = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        self.results[test_key] = res

    @gl.public.write
    def probe_exec_prompt_json(self, snippet: str, test_key: str) -> None:
        def prompt_run() -> str:
            prompt = (
                "You are a code analyzer. Analyze this Python snippet and answer 3 questions strictly in JSON format.\n"
                "Questions:\n"
                "1. J1: Does the snippet recompute results or compare only? (RECOMPUTES / COMPARES_ONLY / UNCLEAR)\n"
                "2. J2: What does acceptance compare? (ENUM_OR_BUCKET / FREE_TEXT_OR_PAYLOAD / UNCLEAR)\n"
                "3. J3: Is input isolated from instructions? (ISOLATED / PARTIAL / NOT_ISOLATED / UNCLEAR)\n\n"
                "Return ONLY a JSON object: {\"answers\": [{\"id\": \"J1\", \"label\": \"...\", \"quote\": \"...\"}, {\"id\": \"J2\", \"label\": \"...\", \"quote\": \"...\"}, {\"id\": \"J3\", \"label\": \"...\", \"quote\": \"...\"}]}\n\n"
                f"CODE SNIPPET:\n```python\n{snippet}\n```"
            )
            raw = gl.nondet.exec_prompt(prompt)
            clean = raw.replace("```json", "").replace("```", "").strip()
            return clean

        decision = gl.eq_principle.strict_eq(prompt_run)
        self.results[test_key] = decision

    @gl.public.view
    def get_result(self, key: str) -> str:
        if key in self.results:
            return self.results[key]
        return ""
