# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class PaginatedView(gl.Contract):
    items: TreeMap[str, str]
    @gl.public.view
    def list_items(self, offset: int, limit: int) -> list[str]:
        return [self.items[str(i)] for i in range(offset, offset + limit)]
