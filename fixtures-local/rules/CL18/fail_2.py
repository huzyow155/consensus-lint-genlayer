# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class FormatPrompt(gl.Contract):
    @gl.public.write
    def analyze(self, code_str: str) -> None:
        p = f"Analyze: {code_str}"
        sand = gl.vm.spawn_sandbox(lambda: gl.nondet.exec_prompt(p))
