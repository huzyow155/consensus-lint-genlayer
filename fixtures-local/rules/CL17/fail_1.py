# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class UnpaginatedView(gl.Contract):
    items: TreeMap[str, str]
    @gl.public.view
    def list_all(self) -> list[str]:
        return [self.items[str(i)] for i in range(10)]
