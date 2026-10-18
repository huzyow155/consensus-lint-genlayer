# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
class WrappedNondet(gl.Contract):
    @gl.public.write
    def do_fetch(self) -> None:
        def my_fetch():
            return gl.nondet.web.get("https://example.com").status
        sand = gl.vm.spawn_sandbox(my_fetch)
