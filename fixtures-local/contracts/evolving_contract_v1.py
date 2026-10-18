# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class EvolvingContract(gl.Contract):
    owner: str
    messages: TreeMap[str, str]
    meta: TreeMap[str, str]

    def __init__(self):
        self.owner = gl.message.sender_address.as_hex

    def _ensure_meta_init(self) -> None:
        if "msg_count" not in self.meta:
            self.meta["msg_count"] = "0"

    @gl.public.write
    def post_status(self, message: str, ref_url: str) -> None:
        # CL15: substring URL check without urllib.parse
        if not ref_url.startswith("https://"):
            raise gl.vm.UserError("invalid ref_url prefix")

        # CL16: unbounded string parameter message
        self._ensure_meta_init()
        cnt = int(self.meta.get("msg_count", "0"))
        self.messages[str(cnt)] = json.dumps({"msg": message, "url": ref_url})
        self.meta["msg_count"] = str(cnt + 1)

    @gl.public.view
    def get_history(self) -> list[str]:
        # CL17: unpaginated view iterating collection
        cnt = int(self.meta.get("msg_count", "0"))
        return [self.messages[str(i)] for i in range(cnt)]
