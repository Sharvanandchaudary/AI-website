"""
Script to convert backend.py to PostgreSQL-only (remove all SQLite code)
"""

import re

# Read the file
with open('backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all if USE_POSTGRES / else blocks and keep only PostgreSQL code
# This regex pattern matches: if USE_POSTGRES:\n    postgres code\nelse:\n    sqlite code
pattern = r'if USE_POSTGRES:\s*\n(.*?)else:\s*\n(.*?)(?=\n\s{0,4}#|\n\s{0,4}def |\n\s{0,4}@app|\n\s{0,4}conn\.|\n\s{0,4}print|\Z)'

def replace_conditional(match):
    postgres_code = match.group(1)
    # Return just the postgres code, removing one level of indentation
    lines = postgres_code.split('\n')
    dedented = []
    for line in lines:
        if line.startswith('        '):  # 8 spaces
            dedented.append(line[4:])  # Remove 4 spaces
        else:
            dedented.append(line)
    return '\n'.join(dedented)

# Replace all conditionals
content = re.sub(pattern, replace_conditional, content, flags=re.DOTALL)

# Remove USE_POSTGRES variable checks
content = re.sub(r'if USE_POSTGRES:\s*\n\s+', '', content)
content = re.sub(r'USE_POSTGRES = .*\n', '', content)
content = re.sub(r'global USE_POSTGRES\s*\n', '', content)

# Remove SQLite imports
content = re.sub(r'import sqlite3\s*\n', '', content)

# Remove "PostgreSQL" if USE_POSTGRES else "SQLite" patterns
content = re.sub(r"'PostgreSQL' if USE_POSTGRES else 'SQLite'", "'PostgreSQL'", content)
content = re.sub(r'"PostgreSQL" if USE_POSTGRES else "SQLite"', '"PostgreSQL"', content)

# Write back
with open('backend_postgres_only.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Created backend_postgres_only.py")
print("Review it and then rename to backend.py")
