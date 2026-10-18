# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class BoundedParam(gl.Contract):
    @gl.public.write
    def set_label(self, label: str) -> None:
        if len(label) < 3 or len(label) > 80:
            raise gl.vm.UserError("invalid label length")
