# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json
class UnboundedRebuild(gl.Contract):
    map_store: TreeMap[str, str]
    @gl.public.write
    def add_item(self, item: str) -> None:
        raw = self.map_store.get("k", "[]")
        lst = json.loads(raw)
        lst.append(item)
        self.map_store["k"] = json.dumps(lst)
