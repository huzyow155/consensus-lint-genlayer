# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class WrappedRunNondet(gl.Contract):
    @gl.public.write
    def do_call(self) -> None:
        def l_fn(): return "OK"
        def v_fn(res): return True
        gl.vm.run_nondet(l_fn, v_fn)
