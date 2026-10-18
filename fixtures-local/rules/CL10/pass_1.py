# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class CheckedReturn(gl.Contract):
    @gl.public.write
    def audit(self) -> None:
        def l_fn(): return "OK"
        def v_fn(r):
            if not isinstance(r, gl.vm.Return): return False
            sand = gl.vm.spawn_sandbox(lambda: "OK")
            return sand.calldata == r.calldata
        gl.vm.run_nondet_unsafe(l_fn, v_fn)
