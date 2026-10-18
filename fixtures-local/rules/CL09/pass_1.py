# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class GoodRecompute(gl.Contract):
    @gl.public.write
    def do_eval(self) -> None:
        def l_fn(): return gl.nondet.web.get("https://example.com").status
        def v_fn(res):
            if not hasattr(res, "calldata"): return False
            sand = gl.vm.spawn_sandbox(lambda: gl.nondet.web.get("https://example.com").status)
            return sand.calldata == res.calldata
        gl.vm.run_nondet_unsafe(l_fn, v_fn)
