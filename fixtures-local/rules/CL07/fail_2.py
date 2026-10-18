# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class PromptStrictEq(gl.Contract):
    @gl.public.write
    def run_prompt_eq(self) -> None:
        res = gl.eq_principle.strict_eq(lambda: gl.nondet.exec_prompt("hello"))
