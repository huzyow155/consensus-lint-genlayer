# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class NoAppend(gl.Contract):
    map_store: TreeMap[str, str]
    @gl.public.write
    def set_val(self, v: str) -> None:
        if len(v) < 50: self.map_store["k"] = v
