#!/usr/bin/env python3
"""Run every solving script and write an execution record + reproducibility manifest.

Runs `solving/code/q*.py` one by one, captures stdout/stderr, notices which
files appeared or changed under `solving/results` and `solving/figures`, and
writes the whole record to `solving/results/run-log.md`. It also writes
`solving/results/repro-manifest.json`: the actual command, exit code, declared
seeds, dependency versions, and SHA-256 of every input and produced file.

The log is the evidence trail: if a number is not backed by a hashed file
listed here, it did not happen.

Usage:
    python run_all.py                      # run all solving/code/q*.py
    python run_all.py --root PATH          # explicit project root or solving/
    python run_all.py --pattern "q1_*.py"  # subset
    python run_all.py --timeout 900        # per-script limit, seconds
    python run_all.py --python PATH        # interpreter to use

Exit code is 0 only if every script succeeded.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

TRACKED_DIRS = ("results", "figures")
DEP_NAMES = ("numpy", "scipy", "pandas", "matplotlib", "sklearn",
             "statsmodels", "networkx", "pulp", "cvxpy", "openpyxl")
SEED_RE = re.compile(r"(?:seed|random_state)\s*[=:]\s*(-?\d+)", re.IGNORECASE)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def skill_root():
    return Path(__file__).resolve().parents[1]


def find_solving_dir(explicit=None):
    """Resolve the solving/ directory without hard-coding an absolute path."""
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if (candidate / "code").is_dir():
            return candidate                      # already the solving/ dir
        if (candidate / "solving" / "code").is_dir():
            return candidate / "solving"          # project root
        return None

    for base in (Path.cwd().resolve(), Path(__file__).resolve()):
        for parent in [base, *base.parents]:
            candidate = parent / "solving"
            if (candidate / "code").is_dir():
                return candidate
    return None


def check_path_safety(solving):
    """Refuse to write results back into the skill installation directory."""
    root = skill_root().resolve()
    target = solving.resolve()
    if target == root or root in target.parents:
        return f"solving/ ({target}) 位于 skill 目录 {root} 内，拒绝运行"
    if target.name != "solving":
        return f"输出目录不是名为 solving/ 的目录: {target}"
    return None


def snapshot(solving):
    """Map relative path -> sha256 for the tracked output directories."""
    state = {}
    for name in TRACKED_DIRS:
        base = solving / name
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file():
                state[f"{name}/{path.relative_to(base).as_posix()}"] = sha256(path)
    return state


def input_hashes(solving):
    """SHA-256 + size of every file under solving/data (raw and processed)."""
    out = {}
    base = solving / "data"
    if base.is_dir():
        for path in sorted(base.rglob("*")):
            if path.is_file():
                out[f"data/{path.relative_to(base).as_posix()}"] = {
                    "sha256": sha256(path), "size": path.stat().st_size}
    return out


def dep_versions():
    import importlib.metadata as md
    out = {}
    for name in DEP_NAMES:
        try:
            out[name] = md.version(name)
        except md.PackageNotFoundError:
            pass
    return out


def declared_seeds(script):
    try:
        return sorted(set(SEED_RE.findall(script.read_text(encoding="utf-8", errors="replace"))))
    except OSError:
        return []


def diff(before, after):
    created = [p for p in after if p not in before]
    changed = [p for p in after if p in before and after[p] != before[p]]
    return sorted(created), sorted(changed)


def run_script(script, python, cwd, timeout):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MPLBACKEND="Agg")
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            [python, str(script)],
            cwd=str(cwd),
            env=env,
            timeout=timeout,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        code = -1
        out = exc.stdout or ""
        err = (exc.stderr or "") + f"\n[timeout] exceeded {timeout}s"
    return code, out, err, time.perf_counter() - started


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Project root or solving/ directory")
    parser.add_argument("--pattern", default="q*.py", help="Glob under code/ (default q*.py)")
    parser.add_argument("--timeout", type=int, default=1800, help="Per-script seconds")
    parser.add_argument("--python", default=sys.executable, help="Interpreter path")
    args = parser.parse_args()

    solving = find_solving_dir(args.root)
    if solving is None:
        print("[ERROR] solving/ with a code/ subfolder not found. Pass --root.", file=sys.stderr)
        return 1

    unsafe = check_path_safety(solving)
    if unsafe:
        print(f"[ERROR] {unsafe}", file=sys.stderr)
        return 1

    scripts = sorted((solving / "code").glob(args.pattern))
    if not scripts:
        print(f"[ERROR] No scripts matching '{args.pattern}' under {solving / 'code'}",
              file=sys.stderr)
        return 1

    log_path = solving / "results" / "run-log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    inputs = input_hashes(solving)
    deps = dep_versions()

    lines = [
        "# 执行记录",
        "",
        f"- 生成时间：{dt.datetime.now().isoformat(timespec='seconds')}",
        f"- 解释器：{args.python}",
        f"- 平台：{platform.platform()}",
        f"- Python：{platform.python_version()}",
        f"- 脚本目录：`{solving / 'code'}`",
        f"- 输入文件：{len(inputs)} 个（SHA-256 见 `solving/results/repro-manifest.json`）",
        f"- 依赖：{', '.join(f'{k} {v}' for k, v in deps.items()) or '未检测到'}",
        "",
    ]

    print(f"[run_all] {len(scripts)} script(s) under {solving / 'code'}")
    failures = 0
    runs = []
    for script in scripts:
        before = snapshot(solving)
        command = [args.python, str(script)]
        code, out, err, seconds = run_script(script, args.python, solving, args.timeout)
        after = snapshot(solving)
        created, changed = diff(before, after)

        status = "OK" if code == 0 else f"FAIL (exit {code})"
        print(f"[run_all] {script.name}: {status} in {seconds:.1f}s")

        runs.append({
            "script": script.name,
            "command": command,
            "cwd": str(solving),
            "seeds": declared_seeds(script),
            "exit_code": code,
            "seconds": round(seconds, 3),
            "stdout_sha256": hashlib.sha256(out.encode("utf-8", "replace")).hexdigest(),
            "created": created,
            "changed": changed,
            "output_hashes": {p: after[p] for p in created + changed},
        })

        lines += [
            f"## {script.name}",
            "",
            f"- 状态：{status}",
            f"- 命令：`{' '.join(command)}`",
            f"- 声明种子：{', '.join(declared_seeds(script)) or '未检测到'}",
            f"- 耗时：{seconds:.1f}s",
            f"- 新增文件：{', '.join('`' + p + '`' for p in created) or '无'}",
            f"- 更新文件：{', '.join('`' + p + '`' for p in changed) or '无'}",
            "",
            "<details><summary>stdout</summary>",
            "",
            "```text",
            out.rstrip() or "(空)",
            "```",
            "",
            "</details>",
            "",
        ]
        if err.strip():
            lines += [
                "<details><summary>stderr</summary>",
                "",
                "```text",
                err.rstrip(),
                "```",
                "",
                "</details>",
                "",
            ]
        if code != 0:
            failures += 1

    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "interpreter": args.python,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "dependencies": deps,
        "inputs": inputs,
        "runs": runs,
    }
    manifest_path = solving / "results" / "repro-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                             encoding="utf-8")
    print(f"[run_all] log -> {log_path}")
    print(f"[run_all] manifest -> {manifest_path}")

    if failures:
        print(f"[run_all] {failures} script(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
