#!/usr/bin/env python3
"""List the model implementations and combination-case library that the
modeling pipeline draws on.

The pipeline treats three folders at the project root as shared assets:

    resource/   54 个基础模型实现（每个含 .py + .m）—— 建模手选型目录、编程手模板
    code/       45 个组合模型案例（.docx，题目+源码）—— 编程手的进阶素材
    write/      历年获奖论文与解题思路（体积大，可选）—— 审题与写作参考

Use this script to confirm that a model name and code path referenced in
references/model-catalog.md actually exist, or to discover models added later.

Project-root resolution order (first hit wins):
    1. --root / --resource DIR
    2. environment variable MATHSKILL_ROOT
    3. walk up from the current working directory
    4. walk up from this script's own location

Steps 3 and 4 mean the skill keeps working when moved anywhere inside the
project tree. If the skill is installed outside the project, set
MATHSKILL_ROOT or pass --root.

Usage:
    python scan_resources.py                     # list every model folder
    python scan_resources.py --examples          # list the code/ case library
    python scan_resources.py --json              # machine-readable output
    python scan_resources.py --verify PATH...    # check that paths exist
    python scan_resources.py --root DIR          # explicit project root
    python scan_resources.py --resource DIR      # explicit resource/ folder

Exit code is 1 when --verify finds a missing path or nothing resolves.
"""

import argparse
import json
import os
import sys
from pathlib import Path

CASE_SUFFIX = ".docx"


def find_project_root(explicit=None):
    """Resolve the project root without hard-coding an absolute path."""
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if (candidate / "resource").is_dir() or (candidate / "code").is_dir():
            return candidate
        if candidate.name in ("resource", "code") and candidate.parent.is_dir():
            return candidate.parent
        return None

    env = os.environ.get("MATHSKILL_ROOT")
    if env:
        candidate = Path(env).expanduser().resolve()
        if (candidate / "resource").is_dir() or (candidate / "code").is_dir():
            return candidate
        print(f"[WARN] MATHSKILL_ROOT={env} has no resource/ or code/; ignoring",
              file=sys.stderr)

    for base in (Path.cwd().resolve(), Path(__file__).resolve()):
        for parent in [base, *base.parents]:
            if (parent / "resource").is_dir() or (parent / "code").is_dir():
                return parent
    return None


def collect(resource_dir):
    """Return [{dir, name, py, m}] sorted by folder name."""
    entries = []
    for folder in sorted(p for p in resource_dir.iterdir() if p.is_dir()):
        py = sorted(p.name for p in folder.glob("*.py"))
        ml = sorted(p.name for p in folder.glob("*.m"))
        entries.append({
            "dir": folder.name,
            "name": folder.name.split("Matlab+Python")[0].strip(),
            "py": py,
            "m": ml,
        })
    return entries


def collect_cases(code_dir):
    """Return [{category, file, path}] for the combination-model case library."""
    entries = []
    for path in sorted(code_dir.rglob(f"*{CASE_SUFFIX}")):
        parts = path.relative_to(code_dir).parts
        entries.append({
            "category": parts[0] if len(parts) > 1 else "",
            "file": path.name,
            "path": path,
        })
    return entries


def rel(path, root):
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Project root (contains resource/ and code/)")
    parser.add_argument("--resource", help="Path to the resource/ folder")
    parser.add_argument("--examples", action="store_true",
                        help="List the code/ combination-case library")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--verify", nargs="+", metavar="PATH",
                        help="Paths to verify, relative to the project root")
    args = parser.parse_args()

    root = find_project_root(args.root or args.resource)
    if root is None:
        print("[ERROR] project root not found. Pass --root DIR, or set "
              "MATHSKILL_ROOT, or run from inside the project.", file=sys.stderr)
        return 1

    resource_dir = root / "resource"
    code_dir = root / "code"

    if args.verify:
        missing = [p for p in args.verify
                   if not (root / p).exists() and not Path(p).exists()]
        for path in args.verify:
            print(f"[{'MISSING' if path in missing else 'ok'}] {path}")
        if missing:
            print(f"[ERROR] {len(missing)} path(s) not found.", file=sys.stderr)
            return 1
        return 0

    if args.examples:
        if not code_dir.is_dir():
            print(f"[ERROR] no code/ folder under {root}", file=sys.stderr)
            return 1
        cases = collect_cases(code_dir)
        if args.json:
            print(json.dumps({"code": rel(code_dir, root),
                              "count": len(cases),
                              "cases": [{**c, "path": rel(c["path"], root)}
                                        for c in cases]},
                             ensure_ascii=False, indent=2))
            return 0
        print(f"code: {rel(code_dir, root)}")
        print(f"cases: {len(cases)}")
        print()
        category = None
        for c in cases:
            if c["category"] != category:
                category = c["category"]
                print(f"## {category}")
            print(f"  {c['file']}")
        return 0

    if not resource_dir.is_dir():
        print(f"[ERROR] no resource/ folder under {root}", file=sys.stderr)
        return 1

    entries = collect(resource_dir)
    if args.json:
        print(json.dumps({
            "project_root": root.as_posix(),
            "resource": rel(resource_dir, root),
            "models": entries,
            "code_present": code_dir.is_dir(),
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"project root: {root}")
    print(f"resource: {rel(resource_dir, root)}")
    print(f"models: {len(entries)}")
    if code_dir.is_dir():
        print(f"code: {rel(code_dir, root)} "
              f"({len(collect_cases(code_dir))} cases, use --examples)")
    else:
        print("code: (未找到 —— 组合模型案例库可选)")
    print()
    for entry in entries:
        print(f"- {entry['name']}")
        for name in entry["py"]:
            print(f"    py: {rel(resource_dir / entry['dir'] / name, root)}")
        for name in entry["m"]:
            print(f"    m : {rel(resource_dir / entry['dir'] / name, root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
