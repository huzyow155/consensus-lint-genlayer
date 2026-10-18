# scripts/tools/scan_ascii.py
import os
import sys

TARGET_DIRS = ["contracts", "scripts", "tests", "docs"]
EXTENSIONS = [".py", ".js", ".json", ".md"]

def scan_file(filepath):
    non_ascii = []
    with open(filepath, "rb") as f:
        content = f.read()
    for idx, b in enumerate(content, start=1):
        if b > 127:
            non_ascii.append((idx, b))
    return non_ascii

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    total_files = 0
    violations = 0

    print("=== SCANNING FOR NON-ASCII CHARACTERS ===")
    for tdir in TARGET_DIRS:
        full_dir = os.path.join(root_dir, tdir)
        if not os.path.exists(full_dir):
            continue
        for root, _, files in os.walk(full_dir):
            for file in files:
                if any(file.endswith(ext) for ext in EXTENSIONS):
                    fpath = os.path.join(root, file)
                    rel = os.path.relpath(fpath, root_dir)
                    total_files += 1
                    errs = scan_file(fpath)
                    if errs:
                        violations += 1
                        print(f"[FAIL] {rel}: {len(errs)} non-ASCII bytes found (e.g. byte {errs[0][1]} at offset {errs[0][0]})")

    print(f"Scanned {total_files} files. Violations: {violations}")
    if violations > 0:
        sys.exit(1)
    print("ALL SCANNED FILES ARE PURE ASCII: OK")

if __name__ == "__main__":
    main()
