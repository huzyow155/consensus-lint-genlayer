# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import urllib.parse
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
        if not isinstance(message, str) or len(message) < 1 or len(message) > 140:
            raise gl.vm.UserError("invalid message length")

        if not isinstance(ref_url, str) or len(ref_url) < 10 or len(ref_url) > 200:
            raise gl.vm.UserError("invalid ref_url length")

        parsed = urllib.parse.urlsplit(ref_url)
        if parsed.scheme != "https":
            raise gl.vm.UserError("https required")

        self._ensure_meta_init()
        cnt = int(self.meta.get("msg_count", "0"))
        self.messages[str(cnt)] = json.dumps({"msg": message, "url": ref_url})
        self.meta["msg_count"] = str(cnt + 1)

    @gl.public.view
    def get_history(self, offset: int, limit: int) -> list[str]:
        off = max(0, int(offset))
        lim = min(50, max(1, int(limit)))
        cnt = int(self.meta.get("msg_count", "0"))
        return [self.messages[str(i)] for i in range(off, min(cnt, off + lim))]
