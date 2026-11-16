#!/usr/bin/env python3
"""Static contract checks for the tracked Thunar and GTK 3 configuration.

Everything here reads files in the checkout only: no Thunar process, no Xfconf
channel, no display and no live config directory is touched. The checks cover:

* ``thunar/thunarrc`` parses and sets a valid view, sort, hidden-file and
  confirmation policy without enabling recursive writes;
* ``thunar/uca.xml`` parses, has unique actions, and contains no destructive,
  root or recursive custom action;
* ``gtk-3.0/settings.ini`` parses and selects an icon theme, font and dark
  preference without tracking the generated colour sheets;
* the README documents the files owned by the theme engine.
"""

from __future__ import annotations

import configparser
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THUNAR = ROOT / "thunar"
THUNARRC = THUNAR / "thunarrc"
UCA = THUNAR / "uca.xml"
GTK = ROOT / "gtk-3.0"
GTK_SETTINGS = GTK / "settings.ini"
GENERATED_CSS = ("gtk.css", "thunar.css")

VIEWS = {"ThunarDetailsView", "ThunarIconView", "ThunarCompactView"}
SORT_COLUMNS = {
    "THUNAR_COLUMN_NAME",
    "THUNAR_COLUMN_SIZE",
    "THUNAR_COLUMN_SIZE_IN_BYTES",
    "THUNAR_COLUMN_TYPE",
    "THUNAR_COLUMN_DATE_MODIFIED",
    "THUNAR_COLUMN_DATE_ACCESSED",
    "THUNAR_COLUMN_DATE_CREATED",
    "THUNAR_COLUMN_OWNER",
    "THUNAR_COLUMN_GROUP",
    "THUNAR_COLUMN_PERMISSIONS",
    "THUNAR_COLUMN_MIME_TYPE",
}
SORT_ORDERS = {"GTK_SORT_ASCENDING", "GTK_SORT_DESCENDING"}
RECURSIVE_PERMISSIONS = {
    "THUNAR_RECURSIVE_PERMISSIONS_ASK",
    "THUNAR_RECURSIVE_PERMISSIONS_NEVER",
    "ASK",
    "NEVER",
}

# Commands that can destroy data or cross a privilege boundary. The word
# boundaries intentionally accept paths and options around the token.
DANGEROUS_COMMAND = re.compile(
    r"(?<![\w-])(?:sudo|pkexec|doas|su|rm|rmdir|shred|dd|mkfs(?:\.[a-z0-9]+)?"
    r"|wipefs|fdisk|parted|chmod|chown|chgrp|setfacl|mount|umount|rsync|scp"
    r"|mv|cp|tee|truncate)(?![\w-])",
    re.IGNORECASE,
)
RECURSIVE_FLAG = re.compile(r"(?:^|\s)(?:-r|-R|--recursive)(?:\s|$)")
SHELL_CHAIN = re.compile(r"[;&|`<>]|\$\(")
MULTI_TARGET = re.compile(r"%[FDX]")
ROOT_WORD = re.compile(r"\b(?:root|superuser)\b", re.IGNORECASE)

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


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    return None


def read_ini(path: Path) -> configparser.ConfigParser | None:
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    try:
        with path.open(encoding="utf-8") as handle:
            parser.read_file(handle)
    except (OSError, configparser.Error) as error:
        report(False, f"{path.relative_to(ROOT)} parses", str(error))
        return None
    return parser


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def check_thunarrc() -> None:
    name = "thunar/thunarrc"
    if not THUNARRC.is_file():
        report(False, f"{name} exists")
        return
    report(True, f"{name} exists")

    config = read_ini(THUNARRC)
    if config is None:
        return
    report(config.has_section("Configuration"), f"{name} has [Configuration]")
    if not config.has_section("Configuration"):
        return
    values = config["Configuration"]

    for key in ("DefaultView", "LastView"):
        value = values.get(key)
        if value is None:
            continue
        report(value in VIEWS, f"{name} {key} is a supported view", value)
    report(
        values.get("LastView") in VIEWS or values.get("DefaultView") in VIEWS,
        f"{name} selects a view mode",
    )

    report(
        values.get("LastSortColumn") in SORT_COLUMNS,
        f"{name} LastSortColumn is valid",
        str(values.get("LastSortColumn")),
    )
    report(
        values.get("LastSortOrder") in SORT_ORDERS,
        f"{name} LastSortOrder is valid",
        str(values.get("LastSortOrder")),
    )
    report(
        parse_bool(values.get("MiscFoldersFirst")) is True,
        f"{name} keeps folders first",
    )

    hidden = values.get("LastShowHidden", values.get("DefaultShowHidden"))
    report(parse_bool(hidden) is not None, f"{name} sets a hidden-files policy", str(hidden))

    move_confirm = parse_bool(values.get("MiscConfirmMoveToTrash"))
    close_confirm = parse_bool(
        values.get("ConfirmCloseMultipleTabs", values.get("MiscConfirmCloseMultipleTabs"))
    )
    report(move_confirm is True, f"{name} confirms moving to the trash")
    report(close_confirm is True, f"{name} confirms closing multiple tabs")

    recursive = values.get("MiscRecursivePermissions")
    report(
        recursive is not None and recursive.upper() in RECURSIVE_PERMISSIONS,
        f"{name} never applies permissions recursively without asking",
        str(recursive),
    )
    recursive_search = values.get("MiscRecursiveSearch")
    report(
        recursive_search is None or parse_bool(recursive_search) is False,
        f"{name} does not enable recursive search by default",
        str(recursive_search),
    )
    delete_action = values.get("MiscShowDeleteAction")
    report(
        delete_action is None or parse_bool(delete_action) is False,
        f"{name} keeps the permanent-delete action hidden",
        str(delete_action),
    )


def check_uca() -> None:
    name = "thunar/uca.xml"
    if not UCA.is_file():
        report(False, f"{name} exists")
        return
    report(True, f"{name} exists")

    try:
        root = ET.parse(UCA).getroot()
    except (OSError, ET.ParseError) as error:
        report(False, f"{name} parses as XML", str(error))
        return
    report(True, f"{name} parses as XML")
    report(local_name(root.tag) == "actions", f"{name} has an <actions> root")

    actions = [child for child in root if local_name(child.tag) == "action"]
    report(len(actions) >= 2, f"{name} defines at least two custom actions")

    unique_ids: list[str] = []
    for index, action in enumerate(actions, start=1):
        label = f"action {index}"
        children: dict[str, ET.Element] = {}
        for child in action:
            children.setdefault(local_name(child.tag), child)

        for required in ("name", "unique-id", "command", "patterns"):
            element = children.get(required)
            text = (element.text or "").strip() if element is not None else ""
            report(bool(text), f"{name} {label} has <{required}>")

        action_name = (children.get("name").text or "").strip() if "name" in children else ""
        command = (children.get("command").text or "").strip() if "command" in children else ""
        unique_id = (
            (children.get("unique-id").text or "").strip()
            if "unique-id" in children
            else ""
        )
        description = (
            (children.get("description").text or "").strip()
            if "description" in children
            else ""
        )
        patterns = (
            (children.get("patterns").text or "").strip() if "patterns" in children else ""
        )

        if unique_id:
            unique_ids.append(unique_id)
        report(bool(patterns), f"{name} {label} has match patterns", patterns)
        report("%f" in command, f"{name} {label} uses the single-target %f placeholder", command)
        report(
            not MULTI_TARGET.search(command),
            f"{name} {label} avoids multi-target placeholders",
            command,
        )
        report(
            not DANGEROUS_COMMAND.search(command),
            f"{name} {label} has no destructive or privileged command",
            command,
        )
        report(
            not RECURSIVE_FLAG.search(command),
            f"{name} {label} has no recursive flag",
            command,
        )
        report(
            not SHELL_CHAIN.search(command),
            f"{name} {label} does not run a shell pipeline",
            command,
        )
        report(
            not ROOT_WORD.search(f"{action_name} {description}"),
            f"{name} {label} is not a root action",
            f"{action_name} {description}",
        )

    report(
        len(unique_ids) == len(set(unique_ids)),
        f"{name} custom-action unique IDs are unique",
    )


def check_gtk_settings() -> None:
    name = "gtk-3.0/settings.ini"
    if not GTK_SETTINGS.is_file():
        report(False, f"{name} exists")
        return
    report(True, f"{name} exists")

    config = read_ini(GTK_SETTINGS)
    if config is None:
        return
    report(config.has_section("Settings"), f"{name} has [Settings]")
    if not config.has_section("Settings"):
        return
    values = config["Settings"]

    theme = values.get("gtk-theme-name", "").strip()
    report(bool(theme), f"{name} selects a base GTK theme", theme)
    icon = values.get("gtk-icon-theme-name", "").strip()
    report(bool(icon), f"{name} selects an icon theme", icon)
    report(
        not icon.startswith("/") and ".." not in Path(icon).parts,
        f"{name} icon theme is a theme name, not a path",
        icon,
    )
    font = values.get("gtk-font-name", "").strip()
    report(
        bool(re.fullmatch(r".+\s+\d+(?:\.\d+)?", font)),
        f"{name} selects a font family and size",
        font,
    )
    dark = parse_bool(values.get("gtk-application-prefer-dark-theme"))
    report(dark is not None, f"{name} sets the dark preference explicitly", str(dark))

    for directory in (GTK, ROOT / "gtk-4.0"):
        for filename in GENERATED_CSS:
            generated = directory / filename
            report(
                not generated.exists(),
                f"{generated.relative_to(ROOT)} stays out of the checkout",
            )

    docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "README.md", THUNAR / "README.md", GTK / "README.md")
    )
    for generated in (
        "gtk-3.0/gtk.css",
        "gtk-3.0/thunar.css",
        "gtk-4.0/gtk.css",
        "gtk-4.0/thunar.css",
    ):
        report(generated in docs, f"README documents generated {generated}")
    lowered = docs.lower()
    report(
        "padilha-theme" in docs and "maria-padilha-de" in docs,
        "README names the theme engine and its checkout",
    )
    report(
        "must not be edited" in lowered or "never edit" in lowered,
        "README says the generated files must not be edited",
    )


def main() -> int:
    check_thunarrc()
    check_uca()
    check_gtk_settings()
    print(f"\n{checks} checks, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
