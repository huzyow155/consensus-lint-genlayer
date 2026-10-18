# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class DirectPrompt(gl.Contract):
    @gl.public.view
    def bad_direct_prompt(self) -> str:
        return gl.nondet.exec_prompt("say hi")
