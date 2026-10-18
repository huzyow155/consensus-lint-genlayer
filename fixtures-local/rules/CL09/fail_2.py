# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class UnconditionalTrueVal(gl.Contract):
    @gl.public.write
    def do_trust(self) -> None:
        def lead(): return "DATA"
        def val(lead_res):
            return True
        gl.vm.run_nondet_unsafe(lead, val)
