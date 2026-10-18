# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class EnumStrictEq(gl.Contract):
    @gl.public.write
    def run_check(self) -> None:
        def check_status() -> str:
            return "PASS"
        res = gl.eq_principle.strict_eq(check_status)
