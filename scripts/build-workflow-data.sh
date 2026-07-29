#!/bin/bash

# Regenerates every snippets/workflows/**/<name>-data.mdx from the fenced
# ```json block in its <name>.mdx sibling. The .mdx file is the single
# hand-edited source of truth; never edit a -data.mdx directly.
#
# Usage:
#   scripts/build-workflow-data.sh                 # rewrite every out-of-sync -data.mdx
#   scripts/build-workflow-data.sh --check         # exit 1 if any pair is out of sync
#   scripts/build-workflow-data.sh <file.mdx> ...  # (re)build specific ones, creating
#                                                  # the -data.mdx if it doesn't exist
#
# Without file arguments, only existing -data.mdx files are refreshed — snippets
# embedded solely by app pages don't need a data companion, so none is created.
#
# The export name is taken from the existing -data.mdx when present, so
# irregular names survive regeneration. New files get the conventional name:
# camelCase of <dir>-<basename> + "Workflow", collapsing a duplicated leading
# country token (dk/dk-send -> dkSendWorkflow).

python3 - "$@" <<'PY'
import json, pathlib, re, sys

args = sys.argv[1:]
check = args == ["--check"]
targets = [pathlib.Path(a) for a in args if a != "--check"]
errors = changed = processed = 0

sources = targets or sorted(pathlib.Path("snippets/workflows").glob("*/*.mdx"))
for src in sources:
    if src.name.endswith("-data.mdx"):
        continue
    data_file = src.with_name(src.stem + "-data.mdx")
    if not targets and not data_file.exists():
        continue
    processed += 1

    m = re.search(r"^``` *json[^\n]*\n(.*?)\n```\s*$", src.read_text(), re.S | re.M)
    if not m:
        print(f"WARNING: no JSON code block in {src}")
        errors += 1
        continue
    body = m.group(1).strip("\n")
    try:
        json.loads(body)
    except ValueError as e:
        print(f"WARNING: invalid JSON in {src}: {e}")
        errors += 1
        continue

    name = None
    if data_file.exists():
        nm = re.match(r"export const ([A-Za-z0-9_]+) = ", data_file.read_text())
        name = nm.group(1) if nm else None
    if not name:
        dir_tokens = src.parent.name.split("-")
        base_tokens = src.stem.split("-")
        if base_tokens[0] == src.parent.name:
            base_tokens = base_tokens[1:]
        tokens = dir_tokens + base_tokens
        name = tokens[0] + "".join(t.capitalize() for t in tokens[1:]) + "Workflow"

    expected = f"export const {name} = {body};\n"

    if data_file.exists() and data_file.read_text() == expected:
        continue
    changed += 1
    if check:
        print(f"OUT OF SYNC: {data_file}")
    else:
        data_file.write_text(expected)
        print(f"wrote {data_file} ({name})")

print(f"\nChecked: {processed} pairs, out of sync: {changed}, errors: {errors}")
sys.exit(1 if errors or (check and changed) else 0)
PY
