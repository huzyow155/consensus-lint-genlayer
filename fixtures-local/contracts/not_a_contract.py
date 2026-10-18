# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

# This file is a utility library, not a GenLayer intelligent contract class.

def calculate_checksum(data: str) -> str:
    import hashlib
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

class UtilityHelper:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def format_entry(self, val: str) -> str:
        return f"{self.prefix}:{val}"
