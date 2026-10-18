# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json
class DefaultModelFallback(gl.Contract):
    @gl.public.write
    def parse_out(self, raw: str) -> None:
        try:
            res = json.loads(raw)
        except Exception:
            res = {"label": "DEFAULT"}
