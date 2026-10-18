# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class SubstringUrlCheck(gl.Contract):
    @gl.public.write
    def check(self, u: str) -> None:
        if not u.startswith("https://"): raise gl.vm.UserError("invalid url")
