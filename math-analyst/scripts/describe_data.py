#!/usr/bin/env python3
"""Inventory the problem's data attachments for the 剖析简报.

For every csv / xlsx file it reports rows, columns, dtypes, missing counts and
numeric ranges, so the brief's 数据盘点 section is measured rather than guessed.
It only reads — nothing is modified or written back.

Usage:
    python describe_data.py 附件目录
    python describe_data.py 附件/a.csv 附件/b.xlsx
    python describe_data.py 附件 --markdown -o inventory.md

.xls (old binary) needs `xlrd`; if it is missing the file is reported as
unreadable instead of failing the whole run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

DATA_SUFFIXES = (".csv", ".xlsx", ".xls", ".txt", ".json")


def gather(targets):
    files = []
    for t in targets:
        p = Path(t).expanduser()
        if p.is_dir():
            files.extend(sorted(q for q in p.rglob("*")
                                if q.suffix.lower() in DATA_SUFFIXES))
        elif p.is_file():
            files.append(p)
        else:
            print(f"[WARN] not found: {p}", file=sys.stderr)
    return files


def load(path: Path):
    suf = path.suffix.lower()
    if suf == ".csv":
        for enc in ("utf-8-sig", "gbk", "utf-8"):
            try:
                return pd.read_csv(path, encoding=enc), f"csv/{enc}"
            except UnicodeDecodeError:
                continue
        return pd.read_csv(path, encoding="utf-8", errors="replace"), "csv/replace"
    if suf == ".xlsx":
        return pd.read_excel(path, sheet_name=None), "xlsx"
    if suf == ".xls":
        try:
            return pd.read_excel(path, sheet_name=None), "xls"
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"需要 xlrd 才能读 .xls（{exc}）") from exc
    if suf == ".json":
        return pd.read_json(path), "json"
    return pd.read_csv(path, sep=None, engine="python"), "txt/delim"


def summarize(name, df, sheet=None):
    rows, cols = df.shape
    label = f"{name}#{sheet}" if sheet else name
    lines = [f"### {label}", "",
             f"- 形状：{rows} 行 × {cols} 列",
             f"- 缺失：合计 {int(df.isna().sum().sum())} 个", "",
             "| 列名 | 类型 | 缺失 | 非空示例 | 范围 / 取值 |",
             "| --- | --- | --- | --- | --- |"]
    for col in df.columns:
        s = df[col]
        miss = int(s.isna().sum())
        sample = s.dropna().head(1)
        example = str(sample.iloc[0]) if len(sample) else ""
        example = (example[:24] + "…") if len(example) > 25 else example
        if pd.api.types.is_numeric_dtype(s) and s.notna().any():
            rng = f"[{s.min():g}, {s.max():g}]"
        else:
            uniq = s.dropna().unique()
            rng = f"{len(uniq)} 个唯一值" if len(uniq) <= 20 else f"高基数（{len(uniq)}）"
        lines.append(f"| {col} | {s.dtype} | {miss} | {example} | {rng} |")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("targets", nargs="+", help="Files or directories")
    ap.add_argument("--markdown", action="store_true",
                    help="Emit Markdown (default) instead of plain text")
    ap.add_argument("-o", "--out", help="Write to this file instead of stdout")
    args = ap.parse_args(argv)

    files = gather(args.targets)
    if not files:
        print("[ERROR] no data files found", file=sys.stderr)
        return 1

    blocks = ["# 数据盘点", ""]
    unreadable = []
    for path in files:
        try:
            data, how = load(path)
        except Exception as exc:  # noqa: BLE001
            unreadable.append(f"{path.name}: {exc}")
            continue
        if isinstance(data, dict):
            for sheet, df in data.items():
                blocks.append(summarize(path.name, df, sheet))
        else:
            blocks.append(summarize(path.name, data))
        blocks.append(f"> 读取方式：{how}；路径：`{path.as_posix()}`\n")

    text = "\n".join(blocks)
    if unreadable:
        text += "\n## 无法读取\n\n" + "\n".join(f"- {u}" for u in unreadable) + "\n"

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"[ok] wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
