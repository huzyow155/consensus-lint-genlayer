# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import hashlib
import urllib.parse
from datetime import datetime, timezone
from genlayer import *

LABEL_MIN = 3
LABEL_MAX = 80
NOTE_MAX = 200
PAGE_LIMIT_MAX = 50


def _parse_chain_datetime() -> tuple[int, str]:
    if not hasattr(gl, "message_raw") or not isinstance(gl.message_raw, dict):
        raise gl.vm.UserError("clock unavailable")
    raw_dt = gl.message_raw.get("datetime")
    if not raw_dt:
        raise gl.vm.UserError("clock unavailable")
    clean = str(raw_dt).strip()
    try:
        iso_clean = clean[:-1] + "+00:00" if clean.endswith("Z") else clean
        dt = datetime.fromisoformat(iso_clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return int(dt.timestamp()), dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        raise gl.vm.UserError("invalid datetime format")


class GoodHygieneContract(gl.Contract):
    owner: str
    items: TreeMap[str, str]
    item_ids: TreeMap[str, str]
    meta: TreeMap[str, str]

    def __init__(self):
        # Lazy init: no TreeMap assignments in __init__
        self.owner = gl.message.sender_address.as_hex

    def _ensure_meta_init(self) -> None:
        if "total" not in self.meta:
            self.meta["total"] = "0"

    @gl.public.write
    def register_entry(self, label: str, source_url: str) -> None:
        if not isinstance(label, str) or len(label) < LABEL_MIN or len(label) > LABEL_MAX:
            raise gl.vm.UserError("invalid label length")
        if not isinstance(source_url, str) or len(source_url) < 10 or len(source_url) > 300:
            raise gl.vm.UserError("invalid url length")

        parsed = urllib.parse.urlsplit(source_url)
        if parsed.scheme != "https":
            raise gl.vm.UserError("source url must use https")
        if parsed.hostname != "raw.githubusercontent.com":
            raise gl.vm.UserError("source host not allowed")

        ts_int, now_iso = _parse_chain_datetime()
        self._ensure_meta_init()

        def leader_fn() -> str:
            def fetch_call():
                res = gl.nondet.web.get(source_url)
                body = res.body if isinstance(res.body, (bytes, bytearray)) else str(res.body).encode("utf-8")
                return hashlib.sha256(body).hexdigest()
            sand = gl.vm.spawn_sandbox(fetch_call)
            if not isinstance(sand, gl.vm.Return):
                raise gl.vm.UserError("fetch failed")
            return json.dumps({"sha256": sand.calldata, "status": "VERIFIED"}, sort_keys=True)

        def validator_fn(leader_res) -> bool:
            if not isinstance(leader_res, gl.vm.Return):
                return False
            try:
                ldata = json.loads(leader_res.calldata)
            except Exception:
                return False

            def val_fetch():
                res = gl.nondet.web.get(source_url)
                body = res.body if isinstance(res.body, (bytes, bytearray)) else str(res.body).encode("utf-8")
                return hashlib.sha256(body).hexdigest()

            val_sand = gl.vm.spawn_sandbox(val_fetch)
            if not isinstance(val_sand, gl.vm.Return):
                return False
            return val_sand.calldata == ldata.get("sha256")

        consensus_raw = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        entry_id = hashlib.sha256(f"{label}|{now_iso}".encode("utf-8")).hexdigest()[:12]
        tot = int(self.meta.get("total", "0"))
        self.items[entry_id] = json.dumps({"id": entry_id, "label": label, "result": consensus_raw, "at": now_iso})
        self.item_ids[str(tot)] = entry_id
        self.meta["total"] = str(tot + 1)

    @gl.public.view
    def get_entry(self, entry_id: str) -> str:
        if entry_id not in self.items:
            raise gl.vm.UserError("entry not found")
        return self.items[entry_id]

    @gl.public.view
    def list_entries(self, offset: int, limit: int) -> str:
        off = max(0, int(offset))
        lim = min(PAGE_LIMIT_MAX, max(1, int(limit)))
        tot = int(self.meta.get("total", "0"))
        ids = [self.item_ids[str(i)] for i in range(off, min(tot, off + lim))]
        return json.dumps(ids)
