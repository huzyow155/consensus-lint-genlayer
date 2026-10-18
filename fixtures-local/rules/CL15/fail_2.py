# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class InUrlCheck(gl.Contract):
    @gl.public.write
    def check(self, u: str) -> None:
        if "raw.githubusercontent.com" in u: pass
