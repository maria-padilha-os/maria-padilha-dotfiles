#!/usr/bin/env python3
"""Static contract checks for the opt-in Discord theme.

The checks deliberately parse only CSS and documentation. They do not install,
start or patch Discord, Vencord or BetterDiscord, and they need no account,
token, network or client. They enforce the promises the theme makes:

* the stylesheet is plain, self-contained CSS with a BetterDiscord meta header;
* it consumes the generated ``--lilith-*`` palette variables;
* every ``var(--lilith-*)`` has a non-empty fallback and every used property is
  declared in the fallback palette;
* it has no imports, remote URLs, fonts, images, JavaScript or updater logic;
* the directory contains no installer or client-patching file;
* the README documents the opt-in, manual, unsupported status.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISCORD = ROOT / "discord"
THEME = DISCORD / "theme.css"
README = DISCORD / "README.md"

FORBIDDEN_SUFFIXES = {
    ".sh", ".bash", ".zsh", ".fish",
    ".js", ".mjs", ".cjs", ".ts", ".tsx",
    ".py", ".rb", ".pl", ".php",
    ".exe", ".bat", ".cmd", ".ps1",
    ".desktop", ".service", ".timer", ".path",
}

failures = 0
checks = 0


def report(ok: bool, name: str, detail: str = "") -> None:
    global failures, checks
    checks += 1
    if ok:
        print(f"  ok   {name}")
    else:
        failures += 1
        print(f"  FAIL {name}")
        if detail:
            print(f"       {detail}")


def strip_comments(css: str) -> str:
    """Remove /* ... */ comments while preserving strings and line layout."""
    out: list[str] = []
    i = 0
    quote = ""
    while i < len(css):
        ch = css[i]
        if quote:
            out.append(ch)
            if ch == "\\" and i + 1 < len(css):
                out.append(css[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = ""
            i += 1
            continue
        if css.startswith("/*", i):
            end = css.find("*/", i + 2)
            if end < 0:
                out.append(css[i:])
                break
            out.append("\n" * css.count("\n", i, end + 2))
            i = end + 2
            continue
        if ch in "\"'":
            quote = ch
        out.append(ch)
        i += 1
    return "".join(out)


def extract_function(css: str, open_paren: int) -> tuple[str, int | None, int] | None:
    """Return (arguments, first top-level comma offset, closing paren)."""
    depth = 1
    i = open_paren + 1
    start = i
    quote = ""
    first_comma: int | None = None
    while i < len(css):
        ch = css[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return css[start:i], first_comma, i
        elif ch == "," and depth == 1 and first_comma is None:
            first_comma = i
        i += 1
    return None


def find_var_calls(css: str) -> list[tuple[str, str | None, str]]:
    """Yield (property name, fallback text or None, full match) for var()."""
    calls: list[tuple[str, str | None, str]] = []
    for match in re.finditer(r"\bvar\s*\(", css, re.IGNORECASE):
        open_paren = css.find("(", match.start())
        parsed = extract_function(css, open_paren)
        if parsed is None:
            calls.append(("", None, match.group(0)))
            continue
        args, comma, close = parsed
        name = (args if comma is None else css[open_paren + 1:comma]).strip()
        fallback = None if comma is None else css[comma + 1:close].strip()
        calls.append((name, fallback, css[match.start():close + 1]))
    return calls


def fallback_block(css: str) -> str:
    match = re.search(r":where\s*\(\s*:root\s*\)\s*\{", css)
    if not match:
        return ""
    start = match.end()
    depth = 1
    i = start
    quote = ""
    while i < len(css):
        ch = css[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return css[start:i]
        i += 1
    return ""


def check_balanced(name: str, css: str) -> None:
    pairs = {")": "(", "}": "{", "]": "["}
    stack: list[str] = []
    quote = ""
    errors: list[str] = []
    for ch in css:
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != pairs[ch]:
                errors.append(f"unexpected {ch!r}")
                break
            stack.pop()
    if stack:
        errors.append("unclosed " + "".join(stack[-5:]))
    report(not errors, f"{name}: braces and parentheses are balanced", "; ".join(errors))


def check_meta(name: str, raw: str) -> None:
    report(raw.lstrip().startswith("/**"), f"{name}: starts with a BetterDiscord meta block")
    block = re.match(r"\s*/\*\*(.*?)\*/", raw, re.DOTALL)
    text = block.group(1) if block else ""
    for field in ("name", "author", "description", "version"):
        report(
            bool(re.search(rf"@\s*{field}\s+\S", text, re.IGNORECASE)),
            f"{name}: meta has @{field}",
        )


def check_no_imports_or_assets(name: str, css: str) -> None:
    report(not re.search(r"@import\b", css, re.IGNORECASE), f"{name}: no @import")
    report(not re.search(r"\burl\s*\(", css, re.IGNORECASE), f"{name}: no url() asset")
    report(not re.search(r"@font-face\b", css, re.IGNORECASE), f"{name}: no @font-face")
    report(not re.search(r"https?://", css, re.IGNORECASE), f"{name}: no remote URL")


def check_no_client_or_account_access(name: str, css: str) -> None:
    forbidden = {
        "javascript:": r"javascript\s*:",
        "expression()": r"\bexpression\s*\(",
        "behavior": r"\bbehavior\s*:",
        "-moz-binding": r"-moz-binding\s*:",
        "<script": r"<\s*script\b",
        "fetch()": r"\bfetch\s*\(",
        "XMLHttpRequest": r"\bXMLHttpRequest\b",
        "WebSocket": r"\bWebSocket\b",
        "localStorage": r"\blocalStorage\b",
        "sessionStorage": r"\bsessionStorage\b",
        "document.cookie": r"\bdocument\s*\.\s*cookie\b",
        "Authorization": r"\bAuthorization\b",
        "Bearer token": r"\bBearer\b",
        "Discord API endpoint": r"discord\.com/api",
        "webhook": r"\bwebhook\b",
        "eval()": r"\beval\s*\(",
        "token": r"\btoken\b",
    }
    for label, pattern in forbidden.items():
        report(
            not re.search(pattern, css, re.IGNORECASE),
            f"{name}: no {label}",
        )


def check_palette(name: str, css: str) -> None:
    block = fallback_block(css)
    report(bool(block), f"{name}: has a :where(:root) fallback palette")

    declared = set(re.findall(r"(--lilith-[\w-]+)\s*:", block))
    declarations = list(re.finditer(r"(--lilith-[\w-]+)\s*:\s*([^;]+);", block))
    empty = [match.group(1) for match in declarations if not match.group(2).strip()]
    report(not empty, f"{name}: fallback palette declarations are non-empty", ", ".join(empty))

    used: set[str] = set()
    missing_fallback: list[str] = []
    empty_fallback: list[str] = []
    non_lilith: list[str] = []
    for prop, fallback, full in find_var_calls(css):
        if not prop.startswith("--lilith-"):
            non_lilith.append(full)
            continue
        used.add(prop)
        if fallback is None:
            missing_fallback.append(full)
        elif not fallback:
            empty_fallback.append(full)

    report(not non_lilith, f"{name}: every var() uses a --lilith-* property", "; ".join(non_lilith[:5]))
    report(not missing_fallback, f"{name}: every var(--lilith-*) has a fallback", "; ".join(missing_fallback[:5]))
    report(not empty_fallback, f"{name}: no empty --lilith-* fallbacks", "; ".join(empty_fallback[:5]))
    undeclared = sorted(used - declared)
    report(not undeclared, f"{name}: every used --lilith-* property is in the fallback palette", ", ".join(undeclared))
    report(len(used) >= 12, f"{name}: consumes the generated palette ({len(used)} properties)")

    # The theme should actually drive Discord's own tokens, not just define
    # unused variables. These are the common legacy and current surfaces.
    required = (
        "--background-primary",
        "--background-secondary",
        "--background-tertiary",
        "--text-normal",
        "--interactive-normal",
        "--focus-primary",
        "--bg-base-primary",
        "--bg-surface-raised",
        "--border-subtle",
    )
    for token in required:
        report(
            bool(re.search(rf"{re.escape(token)}\s*:\s*var\(--lilith-", css)),
            f"{name}: maps {token} to the generated palette",
        )


def check_readme() -> None:
    if not README.is_file():
        report(False, "discord/README.md exists")
        return
    text = README.read_text(encoding="utf-8")
    lower = text.lower()
    report(bool(text.strip()), "discord/README.md is not empty")

    required = {
        "Vencord": "vencord",
        "BetterDiscord": "betterdiscord",
        "manual installation": "manual",
        "opt-in": "opt-in",
        "unsupported": "unsupported",
        "Terms of Service": "terms of service",
        "no token/account/message access": "token",
        "no auto-update": "auto-update",
        "not installed by this repository": "does **not** install",
    }
    for label, needle in required.items():
        report(needle in lower, f"README documents {label}")

    report("bin/padilha-dots" in text, "README says padilha-dots does not install Discord")
    report("padilha-theme" in text, "README documents the generated palette source")


def check_no_installers() -> None:
    if not DISCORD.is_dir():
        report(False, "discord/ directory exists")
        return
    offenders = sorted(
        str(path.relative_to(ROOT))
        for path in DISCORD.rglob("*")
        if path.is_file() and path.suffix.lower() in FORBIDDEN_SUFFIXES
    )
    report(not offenders, "discord/ contains no installer or client-patching file", ", ".join(offenders))


def main() -> int:
    print("discord theme contract")
    check_no_installers()
    check_readme()

    if not THEME.is_file():
        report(False, "discord/theme.css exists", str(THEME))
        print(f"\n{failures} Discord theme check(s) failed ({checks} run)")
        return 1

    raw = THEME.read_text(encoding="utf-8")
    css = strip_comments(raw)
    report(bool(css.strip()), "theme.css is not empty")
    check_meta("theme.css", raw)
    check_balanced("theme.css", css)
    check_no_imports_or_assets("theme.css", css)
    check_no_client_or_account_access("theme.css", css)
    check_palette("theme.css", css)

    if failures:
        print(f"\n{failures} Discord theme check(s) failed ({checks} run)")
        return 1
    print(f"\n{checks} Discord theme checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
