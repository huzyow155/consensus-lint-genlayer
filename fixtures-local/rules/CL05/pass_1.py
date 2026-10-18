# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class LazyInit(gl.Contract):
    records: TreeMap[str, str]
    def __init__(self):
        pass
    def _ensure(self):
        if "k" not in self.records: self.records["k"] = "v"
