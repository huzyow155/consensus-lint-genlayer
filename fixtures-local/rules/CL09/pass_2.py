# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class AnotherRecompute(gl.Contract):
    @gl.public.write
    def do_audit(self) -> None:
        def lead(): return "HASH"
        def val(lead_res):
            if not hasattr(lead_res, "calldata"): return False
            s = gl.vm.spawn_sandbox(lambda: gl.nondet.exec_prompt("q"))
            return s.calldata == lead_res.calldata
        gl.vm.run_nondet_unsafe(lead, val)
