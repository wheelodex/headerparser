from __future__ import annotations
import re


def ascii_splitlines(s: str) -> list[str]:
    lines = []
    lastend = 0
    for m in re.finditer(r"\r\n?|\n", s):
        lines.append(s[lastend : m.end()])
        lastend = m.end()
    if lastend < len(s):
        lines.append(s[lastend:])
    return lines
