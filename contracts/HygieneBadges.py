# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import hashlib
from datetime import datetime, timezone
from genlayer import *

DISPLAY_NAME_MIN = 3
DISPLAY_NAME_MAX = 60
PAGE_LIMIT_MAX = 50


def _parse_iso8601_utc(dt_str: str) -> tuple[int, str]:
    if not isinstance(dt_str, str):
        raise gl.vm.UserError("datetime must be string")
    clean = dt_str.strip()
    if not clean:
        raise gl.vm.UserError("empty datetime")
    try:
        iso_clean = clean[:-1] + "+00:00" if clean.endswith("Z") else clean
        dt = datetime.fromisoformat(iso_clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return int(dt.timestamp()), dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        raise gl.vm.UserError("invalid ISO-8601 datetime format")


def _get_chain_time() -> tuple[int, str]:
    if hasattr(gl, "message_raw") and isinstance(gl.message_raw, dict):
        raw_dt = gl.message_raw.get("datetime")
        if raw_dt:
            return _parse_iso8601_utc(str(raw_dt))
    raise gl.vm.UserError("clock unavailable")


class HygieneBadges(gl.Contract):
    owner: str
    ledger_address: str
    badges: TreeMap[str, str]
    badge_ids: TreeMap[str, str]
    meta: TreeMap[str, str]

    def __init__(self):
        # Lazy initialization: No TreeMap assignments inside __init__
        self.owner = gl.message.sender_address.as_hex.lower()
        self.ledger_address = ""

    def _ensure_meta_init(self) -> None:
        if "nonce" not in self.meta: self.meta["nonce"] = "0"
        if "badges_total" not in self.meta: self.meta["badges_total"] = "0"

    @gl.public.view
    def get_owner(self) -> str:
        return self.owner

    @gl.public.view
    def get_ledger_address(self) -> str:
        return self.ledger_address

    @gl.public.write
    def set_ledger(self, ledger_address: str) -> None:
        sender = gl.message.sender_address.as_hex.lower()
        if sender != self.owner.lower():
            raise gl.vm.UserError("only owner can set ledger address")

        if self.ledger_address != "":
            raise gl.vm.UserError("ledger address already set")

        if not isinstance(ledger_address, str) or len(ledger_address) != 42:
            raise gl.vm.UserError("invalid ledger contract address format")

        clean = ledger_address.strip()
        if not clean.startswith("0x"):
            raise gl.vm.UserError("invalid ledger contract address format")

        try:
            int(clean[2:], 16)
        except ValueError:
            raise gl.vm.UserError("invalid ledger contract address format")

        self.ledger_address = clean.lower()

    @gl.public.write
    def claim_badge(self, target_id: str, display_name: str) -> None:
        if not self.ledger_address:
            raise gl.vm.UserError("ledger not set")

        if not isinstance(target_id, str) or len(target_id) != 12:
            raise gl.vm.UserError("target not found in ledger")
        tid = target_id.strip()

        if not isinstance(display_name, str):
            raise gl.vm.UserError("invalid display name length")
        clean_name = " ".join(display_name.split())
        if len(clean_name) < DISPLAY_NAME_MIN or len(clean_name) > DISPLAY_NAME_MAX:
            raise gl.vm.UserError("invalid display name length")

        sender = gl.message.sender_address.as_hex.lower()
        self._ensure_meta_init()

        dup_key = f"badge_reg:{tid}:{sender}"
        if dup_key in self.meta:
            raise gl.vm.UserError("badge already claimed for this target and sender")

        try:
            ledger = gl.get_contract_at(Address(self.ledger_address))
            summary_raw = ledger.view().get_target_summary(tid)
            summary = json.loads(summary_raw)
        except gl.vm.UserError as ue:
            if "target not found" in str(ue).lower():
                raise gl.vm.UserError("target not found in ledger")
            raise
        except Exception:
            raise gl.vm.UserError("target not found in ledger")

        latest_score = int(summary.get("latest_score", -1))
        latest_grade = str(summary.get("latest_grade", "N/A"))

        if latest_score < 0 or latest_grade in ["N/A", ""]:
            raise gl.vm.UserError("target has no scored audit")

        now_ts, now_iso = _get_chain_time()
        nonce = int(self.meta.get("nonce", "0")) + 1
        self.meta["nonce"] = str(nonce)

        badge_preimage = f"{tid}|{sender}|{nonce}".encode("utf-8")
        badge_id = hashlib.sha256(badge_preimage).hexdigest()[:12]

        current_status = f"BADGE_{latest_grade}"
        initial_history_entry = {
            "grade": latest_grade,
            "score": latest_score,
            "source_sha256": summary.get("latest_source_sha256", ""),
            "at": now_iso,
            "transition": "INITIAL",
        }

        badge_record = {
            "id": badge_id,
            "target_id": tid,
            "display_name": clean_name,
            "claimer": sender,
            "claimed_at": now_iso,
            "current_status": current_status,
            "current_grade": latest_grade,
            "current_score": latest_score,
            "badge_history": [initial_history_entry],
        }

        self.badges[badge_id] = json.dumps(badge_record, sort_keys=True)
        tot_badges = int(self.meta.get("badges_total", "0"))
        self.badge_ids[str(tot_badges)] = badge_id
        self.meta["badges_total"] = str(tot_badges + 1)
        self.meta[dup_key] = badge_id

    @gl.public.write
    def refresh_badge(self, badge_id: str) -> None:
        if not self.ledger_address:
            raise gl.vm.UserError("ledger not set")

        if not isinstance(badge_id, str) or len(badge_id) != 12:
            raise gl.vm.UserError("badge not found")
        bid = badge_id.strip()
        if bid not in self.badges:
            raise gl.vm.UserError("badge not found")

        badge = json.loads(self.badges[bid])
        tid = badge["target_id"]

        try:
            ledger = gl.get_contract_at(Address(self.ledger_address))
            summary_raw = ledger.view().get_target_summary(tid)
            summary = json.loads(summary_raw)
        except Exception:
            raise gl.vm.UserError("failed to query target from ledger")

        new_score = int(summary.get("latest_score", -1))
        new_grade = str(summary.get("latest_grade", "N/A"))
        new_sha256 = str(summary.get("latest_source_sha256", ""))

        # If latest audit in ledger is NOT_A_CONTRACT or unscored, do not replace scored grade
        if new_score < 0 or new_grade in ["N/A", ""]:
            return

        prev_score = int(badge.get("current_score", -1))
        prev_sha256 = ""
        history = badge.get("badge_history", [])
        if history:
            prev_sha256 = history[-1].get("source_sha256", "")

        # Only update history if source hash or score changed
        if new_sha256 != prev_sha256 or new_score != prev_score:
            now_ts, now_iso = _get_chain_time()
            if new_score > prev_score:
                transition = "IMPROVED"
            elif new_score < prev_score:
                transition = "DOWNGRADED"
            else:
                transition = "UNCHANGED"

            history_entry = {
                "grade": new_grade,
                "score": new_score,
                "source_sha256": new_sha256,
                "at": now_iso,
                "transition": transition,
            }
            if len(history) >= 20:
                history.pop(0)
            history.append(history_entry)

            badge["current_status"] = f"BADGE_{new_grade}"
            badge["current_grade"] = new_grade
            badge["current_score"] = new_score
            badge["badge_history"] = history
            self.badges[bid] = json.dumps(badge, sort_keys=True)

    @gl.public.view
    def get_badge(self, badge_id: str) -> str:
        bid = str(badge_id).strip()
        if bid not in self.badges:
            raise gl.vm.UserError("badge not found")
        return self.badges[bid]

    @gl.public.view
    def list_badge_ids(self, offset: int, limit: int) -> str:
        tot = int(self.meta.get("badges_total", "0"))
        off = max(0, int(offset))
        lim = min(PAGE_LIMIT_MAX, max(1, int(limit)))
        all_ids = [self.badge_ids[str(i)] for i in range(tot)]
        all_ids.reverse()
        return json.dumps(all_ids[off:off + lim])

    @gl.public.view
    def get_meta(self) -> str:
        return json.dumps({
            "nonce": self.meta.get("nonce", "0"),
            "badges_total": self.meta.get("badges_total", "0"),
            "ledger_address": self.ledger_address,
        }, sort_keys=True)
