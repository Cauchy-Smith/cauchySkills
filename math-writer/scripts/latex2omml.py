#!/usr/bin/env python3
"""Convert a LaTeX math subset into OMML, so equations land in a .docx as real
editable Word equations rather than images.

Public API:
    to_omml(latex, display=False) -> str        # OMML XML fragment
    add_math(paragraph, latex, display=False)   # insert into a python-docx paragraph

CLI:
    python latex2omml.py "x^2 + \\frac{a}{b}"      # print OMML
    python latex2omml.py --docx out.docx "..."     # render a probe docx
    python latex2omml.py --selftest                # run the built-in cases

Unsupported constructs raise LatexError instead of silently emitting wrong
markup, so a broken equation is loud rather than plausible.
"""

from __future__ import annotations

import re
import sys
from xml.sax.saxutils import escape, quoteattr

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


class LatexError(ValueError):
    """Raised when the input uses a construct this converter does not support."""


# --------------------------------------------------------------------------- #
# symbol tables
# --------------------------------------------------------------------------- #

GREEK = {
    "alpha": "\u03b1", "beta": "\u03b2", "gamma": "\u03b3", "delta": "\u03b4",
    "epsilon": "\u03b5", "varepsilon": "\u03f5", "zeta": "\u03b6", "eta": "\u03b7",
    "theta": "\u03b8", "vartheta": "\u03d1", "iota": "\u03b9", "kappa": "\u03ba",
    "lambda": "\u03bb", "mu": "\u03bc", "nu": "\u03bd", "xi": "\u03be",
    "pi": "\u03c0", "varpi": "\u03d6", "rho": "\u03c1", "varrho": "\u03f1",
    "sigma": "\u03c3", "varsigma": "\u03c2", "tau": "\u03c4", "upsilon": "\u03c5",
    "phi": "\u03d5", "varphi": "\u03c6", "chi": "\u03c7", "psi": "\u03c8",
    "omega": "\u03c9",
    "Gamma": "\u0393", "Delta": "\u0394", "Theta": "\u0398", "Lambda": "\u039b",
    "Xi": "\u039e", "Pi": "\u03a0", "Sigma": "\u03a3", "Upsilon": "\u03a5",
    "Phi": "\u03a6", "Psi": "\u03a8", "Omega": "\u03a9",
}

OPERATORS = {
    "times": "\u00d7", "cdot": "\u22c5", "div": "\u00f7", "pm": "\u00b1",
    "mp": "\u2213", "ast": "\u2217", "star": "\u22c6", "circ": "\u2218",
    "bullet": "\u2022", "oplus": "\u2295", "ominus": "\u2296", "otimes": "\u2297",
    "odot": "\u2299",
}

RELATIONS = {
    "le": "\u2264", "leq": "\u2264", "ge": "\u2265", "geq": "\u2265",
    "ne": "\u2260", "neq": "\u2260", "approx": "\u2248", "sim": "\u223c",
    "simeq": "\u2243", "equiv": "\u2261", "propto": "\u221d",
    "ll": "\u226a", "gg": "\u226b", "lll": "\u22d8", "ggg": "\u22d9",
    "to": "\u2192", "rightarrow": "\u2192", "leftarrow": "\u2190",
    "leftrightarrow": "\u2194", "Rightarrow": "\u21d2", "Leftarrow": "\u21d0",
    "Leftrightarrow": "\u21d4", "mapsto": "\u21a6",
    "in": "\u2208", "notin": "\u2209", "ni": "\u220b",
    "subset": "\u2282", "subseteq": "\u2286", "supset": "\u2283",
    "supseteq": "\u2287", "cup": "\u222a", "cap": "\u2229",
    "setminus": "\u2216", "emptyset": "\u2205", "varnothing": "\u2205",
    "forall": "\u2200", "exists": "\u2203", "nexists": "\u2204",
    "neg": "\u00ac", "lnot": "\u00ac", "land": "\u2227", "wedge": "\u2227",
    "lor": "\u2228", "vee": "\u2228", "angle": "\u2220", "perp": "\u22a5",
    "parallel": "\u2225", "therefore": "\u2234", "because": "\u2235",
    "triangle": "\u25b3", "square": "\u25a1", "prime": "\u2032",
    "top": "\u22a4", "bot": "\u22a5", "dagger": "\u2020", "ddagger": "\u2021",
    "degree": "\u00b0", "surd": "\u221a", "checkmark": "\u2713",
}

MISC = {
    "partial": "\u2202", "nabla": "\u2207", "infty": "\u221e",
    "ldots": "\u2026", "dots": "\u2026", "cdots": "\u22ef",
    "vdots": "\u22ee", "ddots": "\u22f1",
    "mid": "\u2223", "colon": ":",
}

SYMBOLS = {}
SYMBOLS.update(GREEK)
SYMBOLS.update(OPERATORS)
SYMBOLS.update(RELATIONS)
SYMBOLS.update(MISC)

FUNCTIONS = {
    "sin", "cos", "tan", "cot", "sec", "csc",
    "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh", "coth",
    "log", "ln", "lg", "exp", "det", "dim", "ker", "deg", "gcd",
    "arg", "max", "min", "sup", "inf", "lim", "liminf", "limsup",
    "Pr", "mod", "bmod",
}

NARY = {
    "sum": "\u2211", "prod": "\u220f", "coprod": "\u2210",
    "int": "\u222b", "iint": "\u222c", "iiint": "\u222d", "oint": "\u222e",
    "bigcup": "\u22c3", "bigcap": "\u22c2", "bigoplus": "\u2a01",
}

# big operators that stack limits above/below by default
STACKED = {"sum", "prod", "coprod", "bigcup", "bigcap", "bigoplus"}

ACCENTS = {
    "hat": "\u0302", "widehat": "\u0302", "bar": "\u0304", "overline": "\u0304",
    "tilde": "\u0303", "widetilde": "\u0303", "dot": "\u0307", "ddot": "\u0308",
    "vec": "\u20d7", "acute": "\u0301", "grave": "\u0300",
    "check": "\u030c", "breve": "\u0306", "underline": "\u0332",
}

# control symbols -> literal character
CONTROL_SYMBOLS = {
    "{": "{", "}": "}", "%": "%", "&": "&", "#": "#", "_": "_", "$": "$",
    "|": "\u2016", "-": "-",
}

SPACING = {
    ",": "\u2009", ";": "\u2005", ":": "\u2005", "!": "",
    " ": "\u00a0", "quad": "\u2003", "qquad": "\u2003\u2003",
}

STYLED_WORDS = {
    "text": "p", "mathrm": "p", "operatorname": "p", "mathsf": "p",
    "mathtt": "p", "mathit": "i", "mathbf": "b", "boldsymbol": "bi",
    "mathcal": "p",
}

LITERAL_WORDS = {"text"}  # contents taken verbatim, not parsed as math

DELIMS = {
    "(": "(", ")": ")", "[": "[", "]": "]",
    "\\{": "{", "\\}": "}", "\\lbrace": "{", "\\rbrace": "}",
    "\\langle": "\u27e8", "\\rangle": "\u27e9",
    "|": "|", "\\|": "\u2016", "\\vert": "|", "\\Vert": "\u2016",
    "\\lvert": "|", "\\rvert": "|", "\\lVert": "\u2016", "\\rVert": "\u2016",
    ".": "",
}

ENVIRONMENTS = {"pmatrix", "bmatrix", "matrix", "cases", "aligned", "align", "array"}


# --------------------------------------------------------------------------- #
# tokenizer
# --------------------------------------------------------------------------- #

CONTROL_WORD = re.compile(r"\\([A-Za-z]+)")
_TWO = "\\\\"


class Tok:
    __slots__ = ("kind", "value")

    def __init__(self, kind, value):
        self.kind = kind   # ctrl | csym | char | run | ws
        self.value = value

    def __repr__(self):  # pragma: no cover - debugging aid
        return f"Tok({self.kind},{self.value!r})"


def tokenize(src: str) -> list[Tok]:
    toks: list[Tok] = []
    i = 0
    n = len(src)
    while i < n:
        ch = src[i]
        if ch == "\\":
            if src.startswith(_TWO, i):
                toks.append(Tok("char", "\\\\"))
                i += 2
                continue
            m = CONTROL_WORD.match(src, i)
            if m:
                toks.append(Tok("ctrl", m.group(1)))
                i = m.end()
                continue
            if i + 1 < n:
                toks.append(Tok("csym", src[i + 1]))
                i += 2
                continue
            raise LatexError("dangling backslash at end of input")
        if ch in "{}^_&":
            toks.append(Tok("char", ch))
            i += 1
            continue
        if ch.isspace():
            j = i
            while j < n and src[j].isspace():
                j += 1
            toks.append(Tok("ws", " "))
            i = j
            continue
        j = i
        while j < n and src[j] not in "\\{}^_&" and not src[j].isspace():
            j += 1
        toks.append(Tok("run", src[i:j]))
        i = j
    return toks


# --------------------------------------------------------------------------- #
# AST nodes are plain dicts: {"t": <type>, ...}
# --------------------------------------------------------------------------- #

class Parser:
    def __init__(self, toks: list[Tok]):
        self.toks = toks
        self.i = 0

    # -- token helpers ----------------------------------------------------- #
    def peek(self, skip_ws=True):
        j = self.i
        while j < len(self.toks) and skip_ws and self.toks[j].kind == "ws":
            j += 1
        return self.toks[j] if j < len(self.toks) else None

    def advance(self, skip_ws=True):
        if skip_ws:
            while self.i < len(self.toks) and self.toks[self.i].kind == "ws":
                self.i += 1
        if self.i >= len(self.toks):
            return None
        tok = self.toks[self.i]
        self.i += 1
        return tok

    def at_stop(self, stop):
        tok = self.peek()
        if tok is None:
            return True
        if tok.kind == "char" and tok.value in stop:
            return True
        if tok.kind == "ctrl" and ("\\" + tok.value) in stop:
            return True
        return False

    # -- grammar ----------------------------------------------------------- #
    def parse(self, stop=("./end",)) -> list[dict]:
        nodes = []
        while not self.at_stop(stop):
            tok = self.advance()
            if tok is None:
                break
            if tok.kind == "char" and tok.value == "\\\\":
                nodes.append({"t": "rowbreak"})
                continue
            if tok.kind == "char" and tok.value == "&":
                nodes.append({"t": "align"})
                continue
            node = self.parse_scripts(self.parse_atom(tok))
            if node is not None:
                nodes.append(node)
        return nodes

    def parse_atom(self, tok: Tok):
        if tok is None:
            return None
        if tok.kind == "ws":
            return None
        if tok.kind == "char":
            if tok.value == "{":
                body = self.parse(stop=("}",))
                self.expect_char("}")
                return {"t": "group", "body": body}
            if tok.value == "}":
                raise LatexError("unexpected '}'")
            if tok.value in "_^":
                raise LatexError(f"'{tok.value}' without a base")
            return {"t": "text", "text": tok.value}
        if tok.kind == "csym":
            ch = CONTROL_SYMBOLS.get(tok.value)
            if ch is None:
                ch = SPACING.get(tok.value)
            if ch is None:
                raise LatexError(f"unsupported control symbol '\\{tok.value}'")
            return {"t": "text", "text": ch} if ch else {"t": "empty"}
        if tok.kind == "run":
            return {"t": "text", "text": tok.value}
        if tok.kind == "ctrl":
            return self.parse_control(tok.value)
        raise LatexError(f"unexpected token {tok!r}")

    # -- control words ----------------------------------------------------- #
    def parse_control(self, name: str):
        if name in NARY:
            return self.parse_nary(name)
        if name in ACCENTS:
            arg = self.parse_required_arg()
            return {"t": "acc", "chr": ACCENTS[name], "e": arg}
        if name == "frac" or name == "dfrac" or name == "tfrac":
            num = self.parse_required_arg()
            den = self.parse_required_arg()
            return {"t": "frac", "num": num, "den": den}
        if name in ("binom", "dbinom", "tbinom"):
            num = self.parse_required_arg()
            den = self.parse_required_arg()
            return {"t": "delim", "beg": "(", "end": ")",
                    "e": {"t": "frac", "num": num, "den": den, "nobar": True}}
        if name in SPACING:                      # \quad, \qquad
            return {"t": "text", "text": SPACING[name], "upright": True}
        if name in ("sqrt", "sqrtn"):
            return self.parse_sqrt()
        if name in STYLED_WORDS:
            return self.parse_styled(name)
        if name == "left":
            return self.parse_left_right()
        if name == "right":
            raise LatexError("'\\right' without '\\left'")
        if name == "begin":
            return self.parse_environment()
        if name == "end":
            raise LatexError("'\\end' without '\\begin'")
        if name in ("limits", "nolimits", "displaystyle", "textstyle"):
            return {"t": "empty"}
        if name in ("left.",):
            return {"t": "empty"}
        if name in FUNCTIONS:
            node = {"t": "text", "text": SYMBOLS.get(name, name), "upright": True}
            return node
        if name in SYMBOLS:
            return {"t": "text", "text": SYMBOLS[name]}
        raise LatexError(f"unsupported command '\\{name}'")

    def parse_required_arg(self):
        self.skip_ws()
        tok = self.peek()
        if tok is None:
            raise LatexError("missing required argument")
        if tok.kind == "char" and tok.value == "{":
            self.advance()
            body = self.parse(stop=("}",))
            self.expect_char("}")
            return {"t": "group", "body": body}
        atom = self.parse_atom(self.advance())
        return atom if atom is not None else {"t": "empty"}

    def parse_optional_bracket(self):
        self.skip_ws()
        tok = self.peek()
        if tok is not None and tok.kind == "char" and tok.value == "[":
            self.advance()
            body = self.parse(stop=("]",))
            self.expect_char("]")
            return {"t": "group", "body": body}
        return None

    def parse_sqrt(self):
        deg = self.parse_optional_bracket()
        arg = self.parse_required_arg()
        return {"t": "rad", "deg": deg, "e": arg}

    def parse_styled(self, name: str):
        style = STYLED_WORDS[name]
        if name in LITERAL_WORDS:
            return {"t": "text", "text": self.collect_literal(), "upright": True,
                    "style": style}
        arg = self.parse_required_arg()
        return {"t": "styled", "style": style, "e": arg}

    def collect_literal(self) -> str:
        """Read a {...} group verbatim (for \\text{...}), preserving spaces."""
        self.skip_ws()
        tok = self.advance(skip_ws=False)
        if tok is None or not (tok.kind == "char" and tok.value == "{"):
            # bare single token
            return self._tok_text(tok)
        depth = 1
        parts = []
        while self.i < len(self.toks) and depth:
            tok = self.toks[self.i]
            self.i += 1
            if tok.kind == "char" and tok.value == "{":
                depth += 1
                parts.append("{")
            elif tok.kind == "char" and tok.value == "}":
                depth -= 1
                if depth:
                    parts.append("}")
            else:
                parts.append(self._tok_text(tok))
        return "".join(parts)

    @staticmethod
    def _tok_text(tok) -> str:
        if tok is None:
            return ""
        if tok.kind == "ws":
            return " "
        if tok.kind == "ctrl":
            return SYMBOLS.get(tok.value, tok.value)
        if tok.kind == "csym":
            return CONTROL_SYMBOLS.get(tok.value, tok.value)
        return tok.value

    def parse_nary(self, name: str):
        chr_ = NARY[name]
        node = {"t": "nary", "chr": chr_, "sub": None, "sup": None,
                "e": {"t": "empty"}, "stacked": name in STACKED, "name": name}
        self.skip_ws()
        while True:
            tok = self.peek()
            if tok is not None and tok.kind == "char" and tok.value in "_^":
                self.advance()
                arg = self.parse_required_arg()
                if tok.value == "_":
                    node["sub"] = arg
                else:
                    node["sup"] = arg
                self.skip_ws()
                continue
            if tok is not None and tok.kind == "ctrl" and tok.value in ("limits", "nolimits"):
                self.advance()
                node["stacked"] = tok.value == "limits"
                self.skip_ws()
                continue
            break
        # the operand: one atom, or a group
        tok = self.peek()
        if tok is not None and not self.at_stop(("./end",)):
            nxt = self.peek()
            if nxt.kind == "char" and nxt.value == "{":
                self.advance()
                body = self.parse(stop=("}",))
                self.expect_char("}")
                node["e"] = {"t": "group", "body": body}
            elif nxt.kind == "ctrl" and nxt.value in NARY:
                node["e"] = {"t": "empty"}
            else:
                atom = self.parse_atom(self.advance())
                if atom is not None:
                    node["e"] = self.parse_scripts(atom)
        return node

    def parse_left_right(self):
        beg = self.read_delim()
        body = self.parse(stop=("\\right",))
        tok = self.advance()
        if tok is None or tok.kind != "ctrl" or tok.value != "right":
            raise LatexError("'\\left' without matching '\\right'")
        end = self.read_delim()
        return {"t": "delim", "beg": beg, "end": end, "e": {"t": "group", "body": body}}

    def read_delim(self) -> str:
        self.skip_ws()
        tok = self.advance(skip_ws=False)
        if tok is None:
            raise LatexError("missing delimiter")
        if tok.kind == "ctrl":
            key = "\\" + tok.value
            if key in DELIMS:
                return DELIMS[key]
            raise LatexError(f"unsupported delimiter '\\{tok.value}'")
        if tok.kind == "csym":
            key = "\\" + tok.value
            if key in DELIMS:
                return DELIMS[key]
            raise LatexError(f"unsupported delimiter '\\{tok.value}'")
        if tok.kind == "char" and tok.value in DELIMS:
            return DELIMS[tok.value]
        if tok.kind == "run":
            # a run may start with the delimiter and carry the operand, e.g. "(B"
            head, tail = tok.value[0], tok.value[1:]
            if head in DELIMS:
                if tail:
                    self.toks.insert(self.i, Tok("run", tail))
                return DELIMS[head]
        raise LatexError(f"unsupported delimiter {tok.value!r}")

    def parse_environment(self):
        self.skip_ws()
        name = self.collect_literal().strip()
        if name not in ENVIRONMENTS:
            raise LatexError(f"unsupported environment '{name}'")
        if name == "array":
            self.parse_optional_bracket()      # optional \begin{array}[t]
            self.collect_literal()             # column spec, e.g. {cc}
        rows = self.parse_env_rows(name)
        self.expect_end(name)
        if name in ("aligned", "align"):
            return {"t": "eqarr", "rows": rows}
        if name == "cases":
            return {"t": "delim", "beg": "{", "end": "",
                    "e": {"t": "eqarr", "rows": rows}}
        if name == "pmatrix":
            return {"t": "delim", "beg": "(", "end": ")",
                    "e": {"t": "matrix", "rows": rows}}
        if name == "bmatrix":
            return {"t": "delim", "beg": "[", "end": "]",
                    "e": {"t": "matrix", "rows": rows}}
        return {"t": "matrix", "rows": rows}

    def parse_env_rows(self, env):
        rows = [[]]
        while True:
            tok = self.peek()
            if tok is None:
                raise LatexError(f"unterminated \\begin{{{env}}}")
            if tok.kind == "ctrl" and tok.value == "end":
                break
            if tok.kind == "char" and tok.value == "&":
                self.advance()
                rows[-1].append({"t": "align"})
                continue
            if tok.kind == "char" and tok.value == "\\\\":
                self.advance()
                rows.append([])
                continue
            node = self.parse_scripts(self.parse_atom(self.advance()))
            if node is not None:
                rows[-1].append(node)
        return [r for r in rows]

    def expect_end(self, env):
        self.skip_ws()
        tok = self.advance()
        if tok is None or tok.kind != "ctrl" or tok.value != "end":
            raise LatexError(f"expected \\end{{{env}}}")
        got = self.collect_literal().strip()
        if got != env:
            raise LatexError(f"\\begin{{{env}}} closed by \\end{{{got}}}")

    def parse_scripts(self, base):
        sub = sup = None
        while True:
            tok = self.peek()
            if tok is not None and tok.kind == "char" and tok.value in "_^":
                self.advance()
                arg = self.parse_required_arg()
                if tok.value == "_":
                    sub = arg
                else:
                    sup = arg
                continue
            break
        if sub and sup:
            return {"t": "subsup", "e": base, "sub": sub, "sup": sup}
        if sub:
            return {"t": "sub", "e": base, "sub": sub}
        if sup:
            return {"t": "sup", "e": base, "sup": sup}
        return base

    # -- small helpers ----------------------------------------------------- #
    def skip_ws(self):
        while self.i < len(self.toks) and self.toks[self.i].kind == "ws":
            self.i += 1

    def expect_char(self, ch):
        tok = self.advance()
        if tok is None or tok.kind != "char" or tok.value != ch:
            raise LatexError(f"expected '{ch}'")


# --------------------------------------------------------------------------- #
# OMML emission
# --------------------------------------------------------------------------- #

def _run(text: str, style: str | None = None) -> str:
    if text == "":
        return ""
    preserve = ' xml:space="preserve"' if text != text.strip() else ""
    rpr = f'<m:rPr><m:sty m:val="{style}"/></m:rPr>' if style else ""
    return f"<m:r>{rpr}<m:t{preserve}>{escape(text)}</m:t></m:r>"


def _wrap(tag: str, inner: str, pr: str = "") -> str:
    return f"<m:{tag}>{pr}{inner}</m:{tag}>"


def emit(node, style: str | None = None) -> str:
    """Serialize an AST node. `style` is the inherited math style (p/b/i),
    set by \\mathrm / \\mathbf etc and applied to plain runs underneath."""
    if node is None:
        return ""
    t = node["t"]
    if t == "empty" or t == "rowbreak":
        return ""
    if t == "align":
        return _run("\u00a0\u00a0\u00a0", "p")
    if t == "text":
        return _run(node["text"], "p" if node.get("upright") else style)
    if t == "group":
        return "".join(emit(x, style) for x in node["body"])
    if t == "styled":
        sub = node["style"]
        return "".join(emit(x, sub) for x in _flatten(node["e"]))
    if t == "frac":
        type_pr = '<m:type m:val="noBar"/>' if node.get("nobar") else ""
        return _wrap("f",
                     _wrap("num", emit(node["num"], style))
                     + _wrap("den", emit(node["den"], style)),
                     f"<m:fPr>{type_pr}<m:ctrlPr/></m:fPr>")
    if t == "sup":
        return _wrap("sSup",
                     f'<m:e>{emit(node["e"], style)}</m:e>'
                     f'<m:sup>{emit(node["sup"], style)}</m:sup>',
                     "<m:sSupPr><m:ctrlPr/></m:sSupPr>")
    if t == "sub":
        return _wrap("sSub",
                     f'<m:e>{emit(node["e"], style)}</m:e>'
                     f'<m:sub>{emit(node["sub"], style)}</m:sub>',
                     "<m:sSubPr><m:ctrlPr/></m:sSubPr>")
    if t == "subsup":
        return _wrap("sSubSup",
                     f'<m:e>{emit(node["e"], style)}</m:e>'
                     f'<m:sub>{emit(node["sub"], style)}</m:sub>'
                     f'<m:sup>{emit(node["sup"], style)}</m:sup>',
                     "<m:sSubSupPr><m:ctrlPr/></m:sSubSupPr>")
    if t == "rad":
        deg = node["deg"]
        if deg is None:
            return _wrap("rad", f'<m:deg/><m:e>{emit(node["e"], style)}</m:e>',
                         '<m:radPr><m:degHide m:val="1"/><m:ctrlPr/></m:radPr>')
        return _wrap("rad",
                     f'<m:deg>{emit(deg, style)}</m:deg>'
                     f'<m:e>{emit(node["e"], style)}</m:e>',
                     "<m:radPr><m:ctrlPr/></m:radPr>")
    if t == "nary":
        lim = "undOvr" if node.get("stacked") else "subSup"
        pr = (f'<m:naryPr><m:chr m:val="{quoteattr(node["chr"])[1:-1]}"/>'
              f'<m:limLoc m:val="{lim}"/><m:ctrlPr/></m:naryPr>')
        sub = f'<m:sub>{emit(node["sub"], style)}</m:sub>' if node["sub"] else "<m:sub/>"
        sup = f'<m:sup>{emit(node["sup"], style)}</m:sup>' if node["sup"] else "<m:sup/>"
        return _wrap("nary", f'{sub}{sup}<m:e>{emit(node["e"], style)}</m:e>', pr)
    if t == "delim":
        # both delimiters are always written: an omitted m:endChr makes Word
        # fall back to ")", which is wrong for cases and for \left. ... \right)
        beg, end = node["beg"], node["end"]
        attrs = (f"<m:begChr m:val={quoteattr(beg)}/>"
                 f"<m:endChr m:val={quoteattr(end)}/>")
        return _wrap("d", f'<m:e>{emit(node["e"], style)}</m:e>',
                     f"<m:dPr>{attrs}<m:ctrlPr/></m:dPr>")
    if t == "acc":
        return _wrap("acc", f'<m:e>{emit(node["e"], style)}</m:e>',
                     f'<m:accPr><m:chr m:val={quoteattr(node["chr"])}/><m:ctrlPr/></m:accPr>')
    if t == "eqarr":
        rows = "".join(f'<m:e>{_emit_row(r, style)}</m:e>' for r in node["rows"])
        return _wrap("eqArr", rows, "<m:eqArrPr><m:ctrlPr/></m:eqArrPr>")
    if t == "matrix":
        rws = ""
        for row in node["rows"]:
            cellstr = "".join(
                f'<m:e>{"".join(emit(x, style) for x in cell)}</m:e>'
                for cell in _split(row)
            )
            rws += f"<m:mr>{cellstr}</m:mr>"
        return _wrap("m", rws, "<m:mPr><m:ctrlPr/></m:mPr>")
    raise LatexError(f"cannot emit node type '{t}'")


def _emit_row(nodes, style=None) -> str:
    cells = _split(nodes)
    return _run("\u00a0\u00a0\u00a0", "p").join(
        "".join(emit(n, style) for n in cell) for cell in cells
    )


def _split(nodes) -> list:
    """Split a node list on align markers into cells."""
    cells, cur = [], []
    for n in nodes:
        if n["t"] == "align":
            cells.append(cur)
            cur = []
        elif n["t"] == "rowbreak":
            continue
        else:
            cur.append(n)
    cells.append(cur)
    return cells


def _flatten(node) -> list:
    if node is None:
        return []
    if node["t"] == "group":
        return node["body"]
    return [node]


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #

def to_omml(latex: str, display: bool = False) -> str:
    """Return an OMML fragment for `latex`."""
    if not latex.strip():
        raise LatexError("empty LaTeX input")
    nodes = Parser(tokenize(latex)).parse()
    inner = "".join(emit(n) for n in nodes)
    if not inner:
        raise LatexError("LaTeX produced no output")
    if not display:
        return f'<m:oMath xmlns:m="{M_NS}" xmlns:w="{W_NS}">{inner}</m:oMath>'
    return (
        f'<m:oMathPara xmlns:m="{M_NS}" xmlns:w="{W_NS}">'
        f'<m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr>'
        f"<m:oMath>{inner}</m:oMath></m:oMathPara>"
    )


def add_math(paragraph, latex: str, display: bool = False):
    """Insert an equation into an existing python-docx paragraph."""
    from lxml import etree
    paragraph._p.append(etree.fromstring(to_omml(latex, display=display)))
    return paragraph


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

SELFTEST_CASES = [
    ("x^2 + y_i", None),
    (r"\frac{a+b}{c}", None),
    (r"\sum_{i=1}^{n} x_i", None),
    (r"\int_{0}^{\infty} e^{-x}\,dx", None),
    (r"\sqrt[3]{x+1}", None),
    (r"\hat{\beta} = (X^{\top}X)^{-1}X^{\top}Y", None),
    (r"\alpha \le \beta \ge \gamma \ne \delta", None),
    (r"\left( \frac{1}{n}\sum_{i=1}^{n} (x_i-\bar{x})^2 \right)^{1/2}", None),
    (r"\begin{cases} 1, & x > 0 \\ 0, & x \le 0 \end{cases}", None),
    (r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}", None),
    (r"\lim_{x \to 0} \frac{\sin x}{x} = 1", None),
    (r"\text{覆盖率} = \frac{|S \cap D|}{|D|}", None),
    (r"\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i", None),
    (r"A = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}", None),
    (r"\left. \frac{dy}{dx} \right|_{x=0}", None),
    (r"\left( B^{\top}B \right)^{-1} B^{\top}Y", None),
    (r"\binom{n}{k} = \frac{n!}{k!(n-k)!}", None),
    (r"\min_{x \in S} f(x) \ge 0", None),
    (r"f(x)=\begin{cases} x^2, & x \ge 0 \\ -x, & x<0 \end{cases}", None),
    (r"\mathrm{d}x", None),
    (r"\int_0^T \mathbf{v}\,\mathrm{d}t", None),
    (r"\operatorname{arg\,max}_{\theta} L(\theta)", None),
]


def _selftest():
    bad = 0
    for latex, _ in SELFTEST_CASES:
        try:
            out = to_omml(latex)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL  {latex}\n      {type(exc).__name__}: {exc}")
            bad += 1
            continue
        if "<m:t>" not in out and "<m:t " not in out:
            print(f"EMPTY {latex}")
            bad += 1
            continue
        print(f"ok    {latex}")
    print(f"\n{len(SELFTEST_CASES) - bad}/{len(SELFTEST_CASES)} passed")
    return 1 if bad else 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    if argv[0] == "--selftest":
        return _selftest()
    if argv[0] == "--docx":
        import docx
        from lxml import etree
        out = argv[1]
        doc = docx.Document()
        for latex in argv[2:]:
            p = doc.add_paragraph()
            p._p.append(etree.fromstring(to_omml(latex, display=True)))
        doc.save(out)
        print(f"saved {out}")
        return 0
    for latex in argv:
        print(to_omml(latex))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
