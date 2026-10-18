# scripts/tools/generate_shell_like.py
import os

lines = [
    '# v0.2.16',
    '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }',
    'from genlayer import *',
    '',
    'class ShellContract(gl.Contract):',
    '    owner: str',
    '',
    '    def __init__(self):',
    '        self.owner = gl.message.sender_address.as_hex',
    '',
]

for i in range(1100):
    lines.append(f'    def method_num_{i}(self, val: int) -> int:')
    lines.append(f'        # Pad comment with doc characters to reach oversized byte limit safely {i}')
    lines.append(f'        res = val + {i}')
    lines.append(f'        return res * 2')
    lines.append('')

content = '\n'.join(lines)
target1 = "e:/consensus-lint-fixtures/shell_like.py"
target2 = "fixtures-local/contracts/shell_like.py"

with open(target1, "w", encoding="utf-8") as f:
    f.write(content)

with open(target2, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Generated shell_like.py: {len(content.encode('utf-8'))} bytes")
