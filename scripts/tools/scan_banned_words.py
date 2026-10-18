# scripts/tools/scan_banned_words.py
import os
import sys
import re

TARGET_DIRS = ["contracts", "scripts", "docs"]
FILE_EXTS = [".py", ".js", ".json", ".md"]

BANNED_PHRASES = [
    ("testnet", "Use 'GenLayer Studionet (Preview)' instead of 'testnet'"),
    ("audit certificate", "Never claim 'audit certificate'; this is a linter"),
    ("security guarantee", "Never claim 'security guarantee'"),
    ("verified secure", "Never claim 'verified secure'"),
    ("cryptographic proof", "Never claim 'cryptographic proof'"),
    ("tamper-proof", "Never claim 'tamper-proof'"),
    ("bytecode", "GenVM executes Python, not bytecode"),
    ("unanimous", "Consensus is majority agreement, never claim unanimous"),
]

BANNED_CODE_PATTERNS = [
    (r"\bexec\s*\(", "No dynamic code execution via exec()"),
    (r"\beval\s*\(", "No dynamic code evaluation via eval()"),
    (r"\bcompile\s*\(", "No compile() of untrusted source code"),
    (r"\b__import__\s*\(", "No dynamic import via __import__()"),
]

def check_file(fpath):
    issues = []
    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    is_contract = "contracts" in fpath and fpath.endswith(".py") and not fpath.endswith("Probe.py")

    for idx, line in enumerate(lines, start=1):
        line_lower = line.lower()

        # Check banned wording phrases
        for phrase, reason in BANNED_PHRASES:
            if phrase in line_lower:
                # Ignore this scanning script itself
                if "scan_banned_words.py" in fpath:
                    continue
                issues.append((idx, f"Banned phrase '{phrase}': {reason}", line.strip()[:100]))

        # In contracts, check banned execution patterns
        if is_contract:
            for pat, reason in BANNED_CODE_PATTERNS:
                if re.search(pat, line):
                    # Check if line is just comment or rule string
                    stripped = line.strip()
                    if not stripped.startswith("#") and "No dynamic" not in stripped and "outside string" not in stripped:
                        issues.append((idx, f"Banned execution pattern '{pat}': {reason}", stripped[:100]))

    return issues

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    total_files = 0
    total_violations = 0

    print("=== SCANNING FOR BANNED WORDING AND DANGEROUS CODE PATTERNS ===")
    for tdir in TARGET_DIRS:
        full_dir = os.path.join(root_dir, tdir)
        if not os.path.exists(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            for file in files:
                if any(file.endswith(ext) for ext in FILE_EXTS):
                    fpath = os.path.join(root, file)
                    rel = os.path.relpath(fpath, root_dir)
                    total_files += 1
                    errs = check_file(fpath)
                    if errs:
                        total_violations += len(errs)
                        for line_num, msg, snippet in errs:
                            print(f"[VIOLATION] {rel}:{line_num} -> {msg}")
                            print(f"            Line: {snippet}")

    print(f"\nScanned {total_files} files. Total violations found: {total_violations}")
    if total_violations > 0:
        sys.exit(1)
    print("ALL BANNED WORDING AND SAFETY SCANS PASSED: OK")

if __name__ == "__main__":
    main()
