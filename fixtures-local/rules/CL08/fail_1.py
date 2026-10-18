# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class DirectNondet(gl.Contract):
    @gl.public.write
    def bad_direct_fetch(self) -> None:
        res = gl.nondet.web.get("https://example.com")
