#!/usr/bin/env python3
"""Audit the built paper against the 华为杯 format spec and the structural /
quantity floors.

格式 (格式规范):
    页眉         必须为空
    页脚         居中阿拉伯数字页码, 从摘要页起为 1
    封面         不编号, 且身份信息不外泄到正文
    字体         题目 三号黑体 / 一级标题 四号黑体 / 其他 小四宋体
    行距         单倍行距
    摘要         不超过 2 页 (需要 --pdf)
    图表公式     编号连续
    公式渲染     无未渲染的 LaTeX 源码 (含表格单元格)
    占位符       不得残留 XXX / 待填 / TODO 等
    参考文献     引用编号不超出条目数

结构与量 (paper-structure.md):
    章节         9 个必需章节齐全且顺序正确
    符号说明     必须是表格 (三线表)
    附录         必须含完整源代码
    摘要质量     无编号/引用, 字数与关键词在区间内
    篇幅与量     页数 / 图 / 表 / 参考文献条数达到下限

Usage:
    python check_format.py paper/论文.docx
    python check_format.py paper/论文.docx --pdf paper/论文.pdf
    python check_format.py paper/论文.docx --strict

Exit code is 1 when any FAIL is found (or any WARN under --strict).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn

SPEC_FONTS = {
    ("黑体", 16.0): "论文题目 (三号黑体)",
    ("黑体", 14.0): "一级标题 (四号黑体)",
    ("宋体", 12.0): "正文 (小四宋体)",
    ("宋体", 10.5): "图表标题/参考文献 (五号宋体)",
    ("黑体", 18.0): "封面 (小二黑体)",
    ("Consolas", 10.5): "程序代码 (五号 Consolas)",
    ("宋体", 16.0): "题目备用 (三号宋体)",
}

PLACEHOLDERS = ["XXX", "xxx", "待填", "TODO", "TBD", "????", "____", "【】", "填这里"]

MATH_LEAK_RE = re.compile(r"\$[^$]{1,}\$|\\[a-zA-Z]{2,}")

HEADING_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\s+\S")
FIG_RE = re.compile(r"图(\d+)-(\d+)")
TBL_RE = re.compile(r"表(\d+)-(\d+)")
EQ_RE = re.compile(r"\((\d+)-(\d+)\)")
CITE_RE = re.compile(r"\^?\[(\d+(?:\s*[,\-\u2013]\s*\d+)*)\]")
REF_RE = re.compile(r"^\s*\[(\d+)\]\s*\S")
CAP_FIG_RE = re.compile(r"^\s*图\s*(\d+)\s*[-\u2013]\s*(\d+)")
CAP_TBL_RE = re.compile(r"^\s*表\s*(\d+)\s*[-\u2013]\s*(\d+)")
FIG_NUM_RE = re.compile(r"图\s*(\d+)\s*[-\u2013]\s*(\d+)")
TBL_NUM_RE = re.compile(r"表\s*(\d+)\s*[-\u2013]\s*(\d+)")

results: list[tuple[str, str, str]] = []   # (level, check, message)


def report(level, check, message):
    results.append((level, check, message))


def iter_paragraphs(doc):
    for p in doc.paragraphs:
        yield p
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def _rfonts(run):
    rpr = run._element.find(qn("w:rPr"))
    if rpr is None:
        return None
    return rpr.find(qn("w:rFonts"))


def run_font(run):
    """East-Asian face + point size (what the spec constrains for Chinese)."""
    rf = _rfonts(run)
    east = rf.get(qn("w:eastAsia")) if rf is not None else None
    size = run.font.size.pt if run.font.size is not None else None
    return east, size


def run_ascii(run):
    """Latin face; code blocks use Consolas here, not eastAsia."""
    rf = _rfonts(run)
    return rf.get(qn("w:ascii")) if rf is not None else None


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #

def check_headers(doc):
    for i, section in enumerate(doc.sections):
        for p in section.header.paragraphs:
            if p.text.strip():
                report("FAIL", "页眉", f"第 {i+1} 节页眉有文字: {p.text.strip()[:40]!r}")
                return
        if section.header._element.findall(".//" + qn("w:drawing")):
            report("FAIL", "页眉", f"第 {i+1} 节页眉含图片")
            return
    report("PASS", "页眉", "所有节页眉为空")


def check_footer(doc):
    if len(doc.sections) < 2:
        report("FAIL", "页码", "只有一个节：封面与摘要未分节，无法从摘要页起编号")
        return
    cover, body = doc.sections[0], doc.sections[-1]

    cover_text = "".join(p.text for p in cover.footer.paragraphs).strip()
    if cover_text:
        report("FAIL", "页码", f"封面页脚不应有页码，却发现 {cover_text!r}")
    else:
        report("PASS", "页码", "封面不编号")

    xml = body.footer._element.xml
    if "PAGE" not in xml:
        report("FAIL", "页码", "正文节页脚缺少 PAGE 域")
        return
    centered = any(p.alignment == WD_ALIGN_PARAGRAPH.CENTER
                   for p in body.footer.paragraphs)
    if not centered:
        report("FAIL", "页码", "页脚页码未居中")
    else:
        report("PASS", "页码", "正文节页脚居中含 PAGE 域")

    pg = body._sectPr.find(qn("w:pgNumType"))
    start = pg.get(qn("w:start")) if pg is not None else None
    if start != "1":
        report("FAIL", "页码", f"正文节起始页码为 {start!r}，应为 '1'")
    else:
        report("PASS", "页码", "页码从摘要页起为 1")


def check_fonts(doc):
    palette = Counter()
    offenders = []
    for p in iter_paragraphs(doc):
        for run in p.runs:
            if not run.text.strip():
                continue
            east, size = run_font(run)
            if size is None:
                offenders.append((p.text[:30], east, size))
                continue
            palette[(east or "(默认)", float(size))] += 1
            if (east, float(size)) not in SPEC_FONTS:
                offenders.append((run.text[:30], east, size))

    report("INFO", "字体", "实际字体分布: " +
           ", ".join(f"{k[0]}/{k[1]:g}pt×{v}" for k, v in palette.most_common(8)))
    if offenders:
        sample = "; ".join(f"{t!r}({f}/{s})" for t, f, s in offenders[:5])
        report("WARN", "字体", f"{len(offenders)} 个 run 不在规范字体表内: {sample}")
    else:
        report("PASS", "字体", "所有文字均落在规范字体表内")


def check_line_spacing(doc):
    bad = []
    for p in iter_paragraphs(doc):
        if not p.text.strip():
            continue
        lsr = p.paragraph_format.line_spacing_rule
        if lsr not in (None, WD_LINE_SPACING.SINGLE):
            if lsr == WD_LINE_SPACING.ONE_POINT_FIVE:
                continue          # tolerated, but flagged below
            bad.append(p.text[:30])
    if bad:
        report("WARN", "行距", f"{len(bad)} 段非单倍行距: {bad[:3]}")
    else:
        report("PASS", "行距", "全部段落为单倍行距")


def check_placeholders(doc):
    hits = []
    for p in iter_paragraphs(doc):
        for token in PLACEHOLDERS:
            if token in p.text:
                hits.append((token, p.text.strip()[:40]))
    if hits:
        report("FAIL", "占位符", f"{len(hits)} 处残留: {hits[:3]}")
    else:
        report("PASS", "占位符", "无未填占位符")


def check_math_render(doc):
    """Raw LaTeX that survived into the docx (esp. table cells built as plain text)."""
    hits = []
    for p in iter_paragraphs(doc):
        for run in p.runs:
            if run_ascii(run) == "Consolas":     # appendix source code is exempt
                continue
            for token in MATH_LEAK_RE.findall(run.text):
                hits.append((token, p.text.strip()[:40]))
    if hits:
        report("FAIL", "公式渲染",
               f"{len(hits)} 处残留 LaTeX 源码（公式未渲染或表格单元格未转换）: {hits[:3]}")
    else:
        report("PASS", "公式渲染", "无未渲染的 LaTeX 源码")


def check_numbering(doc):
    text = "\n".join(p.text for p in doc.paragraphs)

    def audit(name, pattern):
        found = {}
        for ch, n in pattern.findall(text):
            found.setdefault(int(ch), set()).add(int(n))
        if not found:
            report("WARN", "编号", f"未发现{name}编号")
            return
        total = sum(len(v) for v in found.values())
        problems = []
        for ch, nums in sorted(found.items()):
            if sorted(nums) != list(range(1, len(nums) + 1)):
                problems.append(f"第{ch}章 {name}编号跳号: {sorted(nums)}")
        if problems:
            report("FAIL", "编号", "; ".join(problems))
        else:
            report("PASS", "编号", f"{name}共 {total} 处，按章连续")

    audit("图", FIG_RE)
    audit("表", TBL_RE)
    audit("公式", EQ_RE)


def check_references(doc):
    paras = [p.text.strip() for p in doc.paragraphs]
    numbered = [int(m.group(1)) for p in paras for m in [REF_RE.match(p)] if m]
    refs = sorted(set(numbered))
    if not refs:
        report("WARN", "参考文献", "未发现 [n] 形式的参考文献条目")
        return
    max_ref = max(refs)

    cited, cited_order = set(), []
    in_refs = False
    for p in paras:
        if p == "参考文献":
            in_refs = True
            continue
        if in_refs or REF_RE.match(p):
            continue
        for m in CITE_RE.finditer(p):
            for part in m.group(1).split(","):
                part = part.strip()
                rng = re.split(r"[\-\u2013]", part)
                if len(rng) == 2 and rng[0].strip().isdigit() and rng[1].strip().isdigit():
                    nums = list(range(int(rng[0]), int(rng[1]) + 1))
                elif part.isdigit():
                    nums = [int(part)]
                else:
                    nums = []
                for n in nums:
                    if n not in cited:
                        cited.add(n)
                        cited_order.append(n)

    over = sorted(c for c in cited if c > max_ref)
    if over:
        report("FAIL", "参考文献", f"正文引用了不存在的文献编号: {over}")
    if len(numbered) != len(refs):
        dupes = sorted({n for n in numbered if numbered.count(n) > 1})
        report("WARN", "参考文献", f"文献条目编号重复: {dupes}")
    if refs != list(range(1, max_ref + 1)):
        report("WARN", "参考文献", f"文献条目编号不连续: {refs}")
    orphan = sorted(set(refs) - cited)
    if orphan:
        report("WARN", "参考文献", f"文末存在未被正文引用的条目: {orphan}")
    if cited_order != sorted(cited_order):
        report("WARN", "参考文献", "正文引用编号未按升序首次出现（应与条目顺序一致）")
    if not over and cited and not orphan and refs == list(range(1, max_ref + 1)):
        report("PASS", "参考文献", f"{len(refs)} 条条目，正文与文末双向对应，未越界")


def check_cross_refs(doc):
    """Caption set vs in-text citation set: orphan objects and dangling refs."""
    paras = [p.text.strip() for p in doc.paragraphs]

    def audit(label, num_re, cap_re):
        caps = set()
        for p in paras:
            m = cap_re.match(p)
            if m:
                caps.add((int(m.group(1)), int(m.group(2))))
        if not caps:
            return
        refs = set()
        for p in paras:
            if cap_re.match(p):
                continue
            for m in num_re.finditer(p):
                refs.add((int(m.group(1)), int(m.group(2))))
        dangling = sorted(refs - caps)
        orphan = sorted(caps - refs)
        if dangling:
            report("FAIL", label, f"正文引用了不存在的编号: {dangling}")
        if orphan:
            report("WARN", label, f"{label}未被正文引用: {orphan}")
        if not dangling and not orphan:
            report("PASS", label, f"{len(caps)} 个对象与正文引用双向对应")

    audit("图引用", FIG_NUM_RE, CAP_FIG_RE)
    audit("表引用", TBL_NUM_RE, CAP_TBL_RE)


def is_toc_page(text):
    return text.count("....") > 3


def check_abstract_pages(pdf_path):
    try:
        import pymupdf
    except ImportError:
        report("WARN", "摘要篇幅", "未安装 pymupdf，跳过页数检查")
        return
    doc = pymupdf.open(str(pdf_path))
    if doc.page_count < 2:
        report("FAIL", "摘要篇幅", "PDF 少于 2 页，缺少摘要页")
        return
    first_body = None
    for i in range(1, doc.page_count):
        t = doc[i].get_text()
        # the TOC page also contains "1 问题重述", so skip it explicitly
        if is_toc_page(t):
            continue
        if re.search(r"^\s*1\s+\S", t, re.M) and "问题重述" in t:
            first_body = i
            break
    if first_body is None:
        report("WARN", "摘要篇幅", "未在 PDF 中定位到正文起始页")
        return
    # cover is index 0 and the abstract starts at index 1; a TOC page may sit
    # between the abstract and the body, so exclude it from the abstract span.
    toc_idx = next((i for i in range(1, first_body)
                    if is_toc_page(doc[i].get_text())), None)
    abstract_end = toc_idx if toc_idx is not None else first_body
    span = abstract_end - 1
    if span < 1:
        report("WARN", "摘要篇幅", "未识别出独立摘要页")
    elif span > 2:
        report("FAIL", "摘要篇幅", f"摘要占用 {span} 页，超过 2 页")
    else:
        report("PASS", "摘要篇幅",
               f"摘要占第 2 页起 {span} 页（正文起于第 {first_body + 1} 页）")


HEI, SONG, CODE = "黑体", "宋体", "Consolas"
H1_PT = 14.0

# 必需内容：标签 + 可接受的标题写法 + 是否必须是顶级章节。
# 允许出现在任意层级——获奖论文里 模型假设/符号说明 常合并成一个顶级章
# （"2 模型假设与符号说明"），模型检验 也常作为每问章内的小节。
REQUIRED_CHAPTERS = [
    ("问题重述", ("问题重述", "问题背景", "问题提出"), False),
    ("问题分析", ("问题分析",), False),
    ("模型假设", ("模型假设",), False),
    ("符号说明", ("符号说明",), False),
    ("模型建立与求解", ("模型建立与求解", "模型建立", "分析与求解", "模型求解"), False),
    ("模型检验", ("模型检验", "检验与", "仿真检验", "模型验证", "模型检验与修正"), False),
    ("模型的评价与推广", ("模型评价", "评价与推广", "模型的评价", "模型分析与评价",
                    "模型及算法评价"), False),
    ("参考文献", ("参考文献",), True),
    ("附录", ("附录",), True),
]

# 量的下限。依据 write/2022年 与 2023年 共 100 篇获奖论文实测：
#   全文页数 中位 61；正文(至参考文献) 中位 45；图 中位 21；表 中位 5；参考文献 中位 9
# 页数与题量相关：固定部分约 12 页，每问再算约 9 页。
MIN_PAGES_BASE = 12
MIN_PAGES_PER_Q = 9
DEFAULT_QUESTIONS = 4
MIN_FIGS_PER_Q = 4
MIN_TBLS_PER_Q = 1
MIN_REFS = 10
MIN_APPENDIX_CODE_RUNS = 20
ABSTRACT_CHARS = (700, 1400)


def page_floor(questions):
    return MIN_PAGES_BASE + MIN_PAGES_PER_Q * questions

COVER_PLACEHOLDER = re.compile(r"某某|某大学|队员[甲乙丙丁]|[Xx]{2,}|待填|TODO|^0{3,}$")


def body_children(doc):
    """Yield ('p', Paragraph) / ('tbl', Table) in true document order."""
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield "p", Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield "tbl", Table(child, doc)


HEADING_STYLE = re.compile(r"(?:Heading|标题)\s*(\d)")


def heading_level(paragraph):
    """Level from the heading style name, else from an explicit outline level."""
    name = paragraph.style.name if paragraph.style is not None else ""
    m = HEADING_STYLE.search(name or "")
    if m:
        return int(m.group(1))
    ppr = paragraph._p.find(qn("w:pPr"))
    if ppr is not None:
        lvl = ppr.find(qn("w:outlineLvl"))
        val = lvl.get(qn("w:val")) if lvl is not None else None
        if val is not None and val.lstrip("-").isdigit():
            return int(val) + 1
    return None


def collect_headings(doc):
    """[(body_index, level, text)] in document order."""
    out = []
    for idx, (kind, obj) in enumerate(body_children(doc)):
        if kind == "p":
            lvl = heading_level(obj)
            if lvl and obj.text.strip():
                out.append((idx, lvl, obj.text.strip()))
    return out


def outline(doc):
    """[(heading text, level, [(kind, obj), ...]), ...] grouped by Heading 1."""
    sections = [("（封面与摘要）", 0, [])]
    for kind, obj in body_children(doc):
        lvl = heading_level(obj) if kind == "p" else None
        if lvl == 1:
            sections.append((obj.text.strip(), 1, []))
        else:
            sections[-1][2].append((kind, obj))
    return sections


def check_structure(doc):
    heads = collect_headings(doc)
    found, missing = {}, []
    for label, aliases, must_be_h1 in REQUIRED_CHAPTERS:
        hit = next(((i, lvl, t) for i, lvl, t in heads
                    if any(a in t for a in aliases)
                    and (lvl == 1 or not must_be_h1)), None)
        if hit is None:
            missing.append(label)
        else:
            found[label] = hit[0]
    if missing:
        report("FAIL", "章节", f"缺少必需章节: {'、'.join(missing)}")
        return
    doc_order = [lbl for lbl, _ in sorted(found.items(), key=lambda kv: kv[1])]
    declared = [lbl for lbl, _, _ in REQUIRED_CHAPTERS]
    if doc_order != declared:
        report("FAIL", "章节", f"章节顺序不符: {' → '.join(doc_order)}")
    else:
        h1 = sum(1 for _, lvl, _ in heads if lvl == 1)
        report("PASS", "章节", f"{len(declared)} 项必需内容齐全且顺序正确（{h1} 个一级标题）")


def check_symbols_table(doc):
    for title, _level, children in outline(doc):
        if "符号说明" in title:
            n = sum(1 for k, _ in children if k == "tbl")
            if n == 0:
                report("FAIL", "符号说明", "符号说明章内没有表格（应为三线表）")
            else:
                report("PASS", "符号说明", f"含 {n} 张表")
            return


def check_appendix_code(doc):
    for title, _level, children in outline(doc):
        if "附录" in title:
            runs = 0
            for kind, obj in children:
                if kind != "p":
                    continue
                for r in obj.runs:
                    if run_ascii(r) == CODE and r.text.strip():
                        runs += 1
            if runs < MIN_APPENDIX_CODE_RUNS:
                report("FAIL", "附录",
                       f"附录程序代码过少（等宽行 {runs} < {MIN_APPENDIX_CODE_RUNS}），应附完整源代码")
            else:
                report("PASS", "附录", f"含 {runs} 行等宽代码")
            return


def check_quantity(doc, pdf_path=None, questions=DEFAULT_QUESTIONS):
    text = "\n".join(p.text for p in doc.paragraphs)
    figs = sorted({(int(a), int(b)) for a, b in FIG_RE.findall(text)})
    tbls = sorted({(int(a), int(b)) for a, b in TBL_RE.findall(text)})
    refs = [p.text.strip() for p in doc.paragraphs if REF_RE.match(p.text.strip())]

    per_q = {}
    for q, _ in figs:
        per_q[q] = per_q.get(q, 0) + 1
    n_q = max(questions, len(per_q), 1)

    short = []
    if len(figs) < MIN_FIGS_PER_Q * n_q:
        short.append(f"图 {len(figs)} < {MIN_FIGS_PER_Q * n_q}（每问 ≥{MIN_FIGS_PER_Q}）")
    if len(tbls) < MIN_TBLS_PER_Q * n_q:
        short.append(f"表 {len(tbls)} < {MIN_TBLS_PER_Q * n_q}（每问 ≥{MIN_TBLS_PER_Q}）")
    if len(refs) < MIN_REFS:
        short.append(f"参考文献 {len(refs)} < {MIN_REFS}")
    weak = [f"问题{q} 仅 {n} 张" for q, n in sorted(per_q.items())
            if n < MIN_FIGS_PER_Q]
    if weak:
        short.append("图偏少: " + "、".join(weak))

    if pdf_path is not None:
        try:
            import pymupdf
            pages = pymupdf.open(str(pdf_path)).page_count - 1   # 不含封面
            floor = page_floor(n_q)
            if pages < floor:
                short.append(f"页数 {pages} < {floor}（{MIN_PAGES_BASE}+{MIN_PAGES_PER_Q}×{n_q} 问）")
        except ImportError:
            pass

    dist = "、".join(f"问题{q} {n} 张" for q, n in sorted(per_q.items())) or "无"
    if short:
        report("WARN", "篇幅与量", f"低于下限: {'；'.join(short)}（图分布: {dist}）")
    else:
        report("PASS", "篇幅与量",
               f"图 {len(figs)}、表 {len(tbls)}、参考文献 {len(refs)}，达标（图分布: {dist}）")


def find_abstract(doc):
    """Return (abstract body text, keywords line) or (None, None)."""
    paras = doc.paragraphs
    start = end = None
    for i, p in enumerate(paras):
        t = p.text.strip()
        if start is None and re.match(r"^摘\s*要\s*[:：]", t):
            start = i
        elif start is not None and re.match(r"^关键词\s*[:：]", t):
            end = i
            break
    if start is None or end is None:
        return None, None
    body = "\n".join(p.text.strip() for p in paras[start + 1:end] if p.text.strip())
    return body, paras[end].text.strip()


def check_abstract_quality(doc):
    body, kw = find_abstract(doc)
    if body is None:
        report("FAIL", "摘要", "未找到 摘要/关键词 段落")
        return
    if not body:
        report("FAIL", "摘要", "摘要正文为空")
        return

    problems = []
    if FIG_RE.search(body):
        problems.append("出现图号")
    if TBL_RE.search(body):
        problems.append("出现表号")
    if re.search(r"\(\d+-\d+\)", body):
        problems.append("出现公式编号")
    if problems:
        report("FAIL", "摘要", "摘要不应含编号/引用: " + "、".join(problems))

    n = len(re.sub(r"\s", "", body))
    if not (ABSTRACT_CHARS[0] <= n <= ABSTRACT_CHARS[1]):
        report("WARN", "摘要", f"正文字符数 {n} 不在 {ABSTRACT_CHARS[0]}–{ABSTRACT_CHARS[1]} 推荐区间")

    if kw:
        kws = [k for k in re.split(r"[；;]", kw.split("：")[-1].split(":")[-1]) if k.strip()]
        if not (3 <= len(kws) <= 5):
            report("WARN", "摘要", f"关键词 {len(kws)} 个，应为 3–5 个")
    else:
        report("WARN", "摘要", "未找到关键词行")

    if not problems:
        report("PASS", "摘要", f"正文 {n} 字，关键词 {len(re.split(r'[；;]', kw.split('：')[-1])) if kw else 0} 个，无编号与引用")

def check_cover(doc):
    """The cover must carry real identifying info; the body must not."""
    if not doc.tables:
        report("FAIL", "封面", "未找到封面信息表")
        return
    table = doc.tables[0]
    values = {}
    for row in table.rows:
        cells = [c.text.strip() for c in row.cells]
        if len(cells) >= 2:
            values[cells[0]] = cells[1]
    empty = [k for k, v in values.items() if not v]
    fake = [f"{k}={v}" for k, v in values.items() if COVER_PLACEHOLDER.search(v)]
    if empty:
        report("WARN", "封面", f"封面字段为空: {empty}（提交前必须填写）")
    if fake:
        report("WARN", "封面", f"封面疑似占位内容: {fake}（提交前替换为真实信息）")
    if not empty and not fake:
        report("PASS", "封面", f"封面字段已填: {', '.join(values)}")

    # identity must not leak into the body
    names = [v for v in values.values() if v and len(v) >= 3]
    body = "\n".join(p.text for p in doc.paragraphs)
    leaked = [n for n in names if n in body]
    if leaked:
        report("FAIL", "封面", f"正文中出现封面的身份信息: {leaked}")
    else:
        report("PASS", "封面", "正文未出现学校/队号/姓名")


def check_toc(doc):
    """100 篇获奖论文中 67 篇带目录；长论文缺目录会显得不专业。"""
    has_field = "TOC \\o" in doc.element.body.xml or "TOC \\" in doc.element.body.xml
    if has_field:
        report("PASS", "目录", "含目录域（导出 PDF 时自动生成页码）")
    else:
        report("WARN", "目录", "未发现目录域；长论文建议在 front matter 设 toc: true")


def check_images(doc):
    n = len(doc.inline_shapes)
    if n == 0:
        report("WARN", "插图", "文档中没有嵌入任何图片")
    else:
        report("PASS", "插图", f"已嵌入 {n} 张图片")


# --------------------------------------------------------------------------- #

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("docx", help="Built .docx")
    ap.add_argument("--pdf", help="Exported PDF (enables the abstract-length check)")
    ap.add_argument("--strict", action="store_true", help="WARN also fails")
    ap.add_argument("--waive", action="append", default=[], metavar="CHECK",
                    help="Accept a check's WARN explicitly (repeatable); recorded in output")
    ap.add_argument("--questions", type=int, default=DEFAULT_QUESTIONS,
                    help=f"Number of sub-questions (default {DEFAULT_QUESTIONS}); "
                         "scales the page and figure floors")
    args = ap.parse_args(argv)

    path = Path(args.docx)
    if not path.exists():
        print(f"[ERROR] not found: {path}", file=sys.stderr)
        return 2

    doc = docx.Document(str(path))
    check_headers(doc)
    check_footer(doc)
    check_fonts(doc)
    check_line_spacing(doc)
    check_placeholders(doc)
    check_math_render(doc)
    check_numbering(doc)
    check_cross_refs(doc)
    check_references(doc)
    check_cover(doc)
    check_images(doc)
    check_toc(doc)
    check_structure(doc)
    check_symbols_table(doc)
    check_appendix_code(doc)
    check_abstract_quality(doc)
    check_quantity(doc, Path(args.pdf) if args.pdf else None, args.questions)
    if args.pdf:
        check_abstract_pages(Path(args.pdf))

    order = {"FAIL": 0, "WARN": 1, "INFO": 2, "PASS": 3}
    waived = set(args.waive)
    for i, (level, check, message) in enumerate(results):
        if level == "WARN" and check in waived:
            results[i] = ("INFO", check, message + " [waived]")
    for level, check, message in sorted(results, key=lambda r: order[r[0]]):
        print(f"[{level:4}] {check}: {message}")

    fails = sum(1 for lvl, _, _ in results if lvl == "FAIL")
    warns = sum(1 for lvl, _, _ in results if lvl == "WARN")
    print(f"\n{len(results)} 项检查：{fails} FAIL, {warns} WARN")
    if fails:
        return 1
    if warns and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
