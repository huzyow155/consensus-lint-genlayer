# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class DirectCalldata(gl.Contract):
    @gl.public.write
    def audit(self) -> None:
        def l_fn(): return "OK"
        def v_fn(r):
            data = r.calldata
            sand = gl.vm.spawn_sandbox(lambda: "OK")
            return sand.calldata == data
        gl.vm.run_nondet_unsafe(l_fn, v_fn)
