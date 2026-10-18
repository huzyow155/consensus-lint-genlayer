# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import urllib.parse
class ParsedUrl(gl.Contract):
    @gl.public.write
    def check_url(self, u: str) -> None:
        p = urllib.parse.urlsplit(u)
        if p.hostname != "github.com":
            raise gl.vm.UserError("host not allowed")
