# v0.1.0
# Intentionally invalid header and dependency line
# Non-ASCII character present: • (bullet)

import json
import datetime
from genlayer import *


class BadHygieneContract(gl.Contract):
    store: TreeMap[str, str]
    items: TreeMap[str, str]

    def __init__(self):
        # CL05: TreeMap assignment in __init__
        self.store["initialized"] = "true"

    @gl.public.write
    def unsafe_write(self, message: str, url: str) -> None:
        # CL16: message: str has no len() check
        # CL15: url prefix check without urllib.parse
        if not url.startswith("https://"):
            # CL14: ValueError instead of gl.vm.UserError
            raise ValueError("invalid url prefix")

        # CL14: assert in public write method
        assert len(url) > 0, "url cannot be empty"

        # CL13: wall-clock time call
        current_time = datetime.datetime.now()

        # CL08: gl.nondet call outside consensus wrapper
        fetch_res = gl.nondet.web.get(url)

        # CL18: public message directly interpolated into prompt without sanitization
        prompt = f"Analyze this user message: {message}"
        raw_model = gl.nondet.exec_prompt(prompt)

        # CL12: model output parsed with default fallback in except
        try:
            parsed = json.loads(raw_model)
        except Exception:
            parsed = {"status": "DEFAULT_FALLBACK"}

        # CL06: unbounded list load-append-store
        raw_list = self.store.get("events", "[]")
        event_list = json.loads(raw_list)
        event_list.append(str(parsed))
        self.store["events"] = json.dumps(event_list)

        # CL07: strict_eq on dynamic json.dumps payload
        def bad_strict():
            return json.dumps({"payload": message, "time": str(current_time)})
        res = gl.eq_principle.strict_eq(bad_strict)

        # CL09, CL10, CL11: flawed validator pattern
        def leader_fn():
            return "LEADER_PAYLOAD"

        def validator_fn(leader_res):
            # CL10: accessed .calldata without checking isinstance(leader_res, gl.vm.Return)
            data = leader_res.calldata
            try:
                # CL09: does not independently recompute verdict, only checks leader data
                valid = (data == "LEADER_PAYLOAD")
                return valid
            except Exception:
                # CL11: waves through failure in except
                return True

        gl.vm.run_nondet_unsafe(leader_fn, validator_fn)

    @gl.public.view
    def get_all_records(self) -> list[str]:
        # CL17: unpaginated view iterating collection
        return [self.items[str(i)] for i in range(10)]
