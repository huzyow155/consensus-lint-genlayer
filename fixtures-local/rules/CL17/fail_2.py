# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class UnpaginatedLoop(gl.Contract):
    store: TreeMap[str, str]
    @gl.public.view
    def get_everything(self) -> list[str]:
        res = []
        for k in self.store:
            res.append(self.store[k])
        return res
