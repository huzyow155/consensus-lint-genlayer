# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json
class JsonDumpStrictEq(gl.Contract):
    @gl.public.write
    def run_bad_eq(self) -> None:
        def leader_calc():
            return json.dumps({"status": "ok", "count": 10})
        res = gl.eq_principle.strict_eq(leader_calc)
