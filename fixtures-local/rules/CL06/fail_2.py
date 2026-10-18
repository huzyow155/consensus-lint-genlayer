# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json
class AnotherUnbounded(gl.Contract):
    data: TreeMap[str, str]
    @gl.public.write
    def push(self, val: str) -> None:
        cur = json.loads(self.data.get("list", "[]"))
        cur.append(val)
        self.data["list"] = json.dumps(cur)
