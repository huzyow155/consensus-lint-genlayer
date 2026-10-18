# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class CleanErrors(gl.Contract):
    @gl.public.write
    def test(self, x: int) -> None:
        if x <= 0:
            raise gl.vm.UserError("x must be positive")
