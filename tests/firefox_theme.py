#!/usr/bin/env python3
"""Contract checks for the tracked Firefox chrome/content stylesheets.

These are static checks on purpose: they run in CI without a real profile,
Firefox session, display or network. They cover the three promises the theme
makes to the rest of the checkout:

* every @import is local, safe and resolves once the generated palette exists;
* every var(--lilith-*) reference has a non-empty fallback, and every used
  property is declared in the fallback palette block;
* no remote asset is referenced;
* every rule in userContent.css is inside an @-moz-document scope.
"""

from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = ROOT / "firefox" / "chrome"
SHEETS = (CHROME / "userChrome.css", CHROME / "userContent.css")
GENERATED_PALETTE = "lilith.css"

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


def check_imports(name: str, css: str) -> list[str]:
    imports: list[str] = []
    for match in re.finditer(r"@import\s+([^;]+);", css, re.IGNORECASE):
        raw = match.group(1).strip()
        url_match = re.fullmatch(
            r"url\s*\(\s*(?:\"([^\"]+)\"|'([^']+)'|([^)\s]+))\s*\)", raw, re.IGNORECASE
        )
        if url_match:
            target = next(group for group in url_match.groups() if group is not None)
        elif len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
            target = raw[1:-1]
        else:
            report(False, f"{name}: import syntax", raw)
            continue
        imports.append(target)
        remote = bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)) or target.startswith("//") or target.startswith("/")
        inside = ".." not in Path(target).parts
        report(not remote and inside, f"{name}: import {target!r} is local", "remote, absolute or parent-relative import")
        resolved = (CHROME / target).resolve()
        try:
            resolved.relative_to(CHROME.resolve())
            contained = True
        except ValueError:
            contained = False
        report(contained, f"{name}: import {target!r} stays inside chrome/")
        if resolved.exists():
            report(True, f"{name}: import {target!r} resolves in the checkout")
        elif target == GENERATED_PALETTE:
            readme = (ROOT / "firefox" / "README.md").read_text(encoding="utf-8")
            documented = GENERATED_PALETTE in readme and "padilha-theme" in readme
            report(documented, f"{name}: import {target!r} is the documented generated palette", "README does not describe the generated palette contract")
        else:
            report(False, f"{name}: import {target!r} resolves", str(resolved))

    # Exercise the same imports against a disposable profile layout where the
    # generated palette exists. This is the layout Firefox actually reads.
    with tempfile.TemporaryDirectory(prefix="padilha-firefox-imports-") as tmp:
        chrome = Path(tmp) / "chrome"
        chrome.mkdir()
        for sheet in SHEETS:
            shutil.copy2(sheet, chrome / sheet.name)
        (chrome / GENERATED_PALETTE).write_text("/* generated palette stub */\n", encoding="utf-8")
        for target in imports:
            target_path = (chrome / target).resolve()
            try:
                target_path.relative_to(chrome.resolve())
                contained = True
            except ValueError:
                contained = False
            report(contained and target_path.is_file(), f"{name}: import {target!r} resolves in an installed profile", str(target_path))

    report(GENERATED_PALETTE in imports, f"{name}: imports the generated palette")
    return imports


def check_variables(name: str, css: str) -> None:
    block = fallback_block(css)
    report(bool(block), f"{name}: has a :where(:root) fallback palette")
    declared = set(re.findall(r"(--lilith-[\w-]+)\s*:", block))
    declarations = list(re.finditer(r"(--lilith-[\w-]+)\s*:\s*([^;]+);", block))
    empty = [match.group(1) for match in declarations if not match.group(2).strip()]
    report(not empty, f"{name}: fallback palette declarations are non-empty", ", ".join(empty))

    used: set[str] = set()
    missing_fallback: list[str] = []
    empty_fallback: list[str] = []
    for prop, fallback, full in find_var_calls(css):
        if not prop.startswith("--lilith-"):
            continue
        used.add(prop)
        if fallback is None:
            missing_fallback.append(full)
        elif not fallback:
            empty_fallback.append(full)

    report(not missing_fallback, f"{name}: every var(--lilith-*) has a fallback", "; ".join(missing_fallback[:5]))
    report(not empty_fallback, f"{name}: no empty --lilith-* fallbacks", "; ".join(empty_fallback[:5]))
    undeclared = sorted(used - declared)
    report(not undeclared, f"{name}: every used --lilith-* property is in the fallback palette", ", ".join(undeclared))


def check_remote_assets(name: str, css: str) -> None:
    remote = re.findall(r"https?://|//[a-zA-Z0-9]", css, re.IGNORECASE)
    report(not remote, f"{name}: no remote URLs", ", ".join(remote[:5]))
    unsafe: list[str] = []
    for match in re.finditer(r"url\s*\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^)]*))\s*\)", css, re.IGNORECASE):
        target = next((group for group in match.groups() if group is not None), "").strip()
        if not target:
            unsafe.append(match.group(0))
        elif re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) and not target.lower().startswith("about:"):
            unsafe.append(target)
        elif target.startswith("//") or target.startswith("/"):
            unsafe.append(target)
    report(not unsafe, f"{name}: no remote url() assets", ", ".join(unsafe[:5]))
    report("@font-face" not in css.lower(), f"{name}: no font assets")


def check_scoping(name: str, css: str) -> None:
    text = strip_comments(css)
    stack: list[str] = []
    scoped = 0
    buf: list[str] = []
    errors: list[str] = []
    for ch in text:
        if ch == "{":
            prelude = " ".join("".join(buf).split())
            if prelude.lower().startswith("@-moz-document"):
                stack.append("moz")
                scoped += 1
            elif prelude.startswith("@"):
                stack.append("at")
            else:
                stack.append("rule")
                if scoped == 0:
                    errors.append(prelude[:100])
            buf = []
        elif ch == "}":
            if not stack:
                errors.append("unmatched closing brace")
            else:
                kind = stack.pop()
                if kind == "moz":
                    scoped -= 1
            buf = []
        elif ch == ";":
            buf = []
        else:
            buf.append(ch)
    if stack:
        errors.append("unclosed block")
    report(not errors, f"{name}: every rule is scoped with @-moz-document", "; ".join(errors[:5]))

    for match in re.finditer(r"@-moz-document\s+([^{]+)\{", text, re.IGNORECASE):
        prelude = " ".join(match.group(1).split())
        remote = bool(re.search(r"https?://|//[a-zA-Z0-9]", prelude, re.IGNORECASE))
        report(not remote, f"{name}: @-moz-document scope is local", prelude[:100])


def main() -> int:
    print("firefox theme contract")
    for sheet in SHEETS:
        name = sheet.name
        if not sheet.is_file():
            report(False, f"{name}: stylesheet exists", str(sheet))
            continue
        raw = sheet.read_text(encoding="utf-8")
        css = strip_comments(raw)
        report(bool(css.strip()), f"{name}: stylesheet is not empty")
        report(css.lstrip().startswith("@import"), f"{name}: @import statements come first")
        check_balanced(name, css)
        check_imports(name, css)
        check_variables(name, css)
        check_remote_assets(name, css)
        if name == "userContent.css":
            check_scoping(name, css)

    if failures:
        print(f"\n{failures} Firefox theme check(s) failed ({checks} run)")
        return 1
    print(f"\n{checks} Firefox theme checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
