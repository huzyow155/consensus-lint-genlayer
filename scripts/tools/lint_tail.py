# scripts/tools/lint_tail.py
import os
import sys

sys.path.append(os.path.dirname(__file__))
from local_lint import lint_source

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    contract_path = os.path.join(root_dir, "contracts", "ConsensusLint.py")
    
    with open(contract_path, "r", encoding="utf-8") as f:
        full_source = f.read()

    # Byte 60,000 cutoff
    source_bytes = full_source.encode("utf-8")
    truncated_bytes = source_bytes[:60000]
    tail_bytes = source_bytes[60000:]
    
    print(f"Full source bytes: {len(source_bytes)}")
    print(f"Truncated portion bytes: {len(truncated_bytes)}")
    print(f"Unlinted tail bytes: {len(tail_bytes)}")
    
    # Complete tail to a valid standalone GenLayer contract module
    # View methods in the tail: list_target_ids, list_series, get_board, get_rule_stats
    lines = full_source.split("\n")
    # Find boundary where clean method starts after byte 60,000 (line 1328 is list_target_ids)
    tail_source_lines = lines[1327:]
    
    tail_contract = (
        '# v0.2.16\n'
        '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\n'
        'import json\n'
        'from genlayer import *\n\n'
        'PAGE_LIMIT_MAX = 50\n\n'
        'class ConsensusLintTail(gl.Contract):\n'
        '    meta: TreeMap[str, str]\n'
        '    targets: TreeMap[str, str]\n'
        '    audits: TreeMap[str, str]\n\n'
        + "\n".join(tail_source_lines)
    )

    mode, findings, score, grade = lint_source(tail_contract)
    print("\n=== UNLINTED TAIL LOCAL LINT RESULT ===")
    print(f"Mode: {mode}")
    print(f"Score: {score}")
    print(f"Grade: {grade}")
    print(f"Findings ({len(findings)}):")
    for rid, f_data in findings.items():
        print(f"  - {rid} ({f_data['severity']}): {f_data['count']} occurrence(s)")
        for it in f_data["items"]:
            print(f"      Line {it['line']}: {it['snippet']}")

    return {
        "score": score,
        "grade": grade,
        "findings": findings,
    }

if __name__ == "__main__":
    main()
