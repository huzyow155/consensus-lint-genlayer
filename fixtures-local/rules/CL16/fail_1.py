# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class UnboundedParam(gl.Contract):
    data: TreeMap[str, str]
    @gl.public.write
    def set_note(self, note: str) -> None:
        self.data["note"] = note
