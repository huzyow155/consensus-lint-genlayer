# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


class MixedHygieneContract(gl.Contract):
    owner: str
    items: TreeMap[str, str]
    meta: TreeMap[str, str]

    def __init__(self):
        self.owner = gl.message.sender_address.as_hex

    def _ensure_meta_init(self) -> None:
        if "nonce" not in self.meta:
            self.meta["nonce"] = "0"

    @gl.public.write
    def update_profile(self, display_name: str, site_url: str) -> None:
        # Proper length check for display_name
        if not isinstance(display_name, str) or len(display_name) < 3 or len(display_name) > 50:
            raise gl.vm.UserError("invalid display_name length")

        # CL15: substring URL check without urllib.parse
        if not site_url.startswith("https://"):
            raise gl.vm.UserError("site_url must start with https://")

        # CL16: site_url has no length check
        sender = gl.message.sender_address.as_hex
        self.items[sender] = json.dumps({"name": display_name, "url": site_url})

    @gl.public.view
    def get_all_profiles(self) -> list[str]:
        # CL17: unpaginated view iterating collection
        res = []
        for k in self.items:
            res.append(self.items[k])
        return res
