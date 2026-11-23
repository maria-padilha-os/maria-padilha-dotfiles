#!/usr/bin/env python3
"""Contract checks for the tracked application theme fallbacks.

These are static checks: they read the checkout and the tracked palette only.
They cover the files that `padilha-theme` owns after the first apply (cava,
fuzzel, btop, Spicetify, micro) plus the GTK 3/4 settings. The goal is to keep
the fresh-clone fallbacks on the same roles as `hypr/scheme/current.lua` and to
make sure the generated colour sheets never enter the repository.
"""

from __future__ import annotations

import configparser
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ROOT / "hypr" / "scheme" / "current.lua"
CAVA = ROOT / "cava" / "config"
FUZZEL = ROOT / "fuzzel" / "fuzzel.ini"
BTOP = ROOT / "btop" / "themes" / "caelestia.theme"
SPICE_CONFIG = ROOT / "spicetify" / "config-xpui.ini"
SPICE_COLOURS = ROOT / "spicetify" / "Themes" / "caelestia" / "color.ini"
MICRO = ROOT / "micro" / "colorschemes" / "padilha.micro"
GTK3 = ROOT / "gtk-3.0" / "settings.ini"
GTK4 = ROOT / "gtk-4.0" / "settings.ini"
COVERAGE = ROOT / "docs" / "app-theme-coverage.md"
FOLLOW_UP = ROOT / "docs" / "maria-padilha-de-follow-up.md"
VISUAL = ROOT / "docs" / "app-theme-visual-checklist.md"

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


def load_palette() -> dict[str, str]:
    if not PALETTE.is_file():
        return {}
    text = PALETTE.read_text(encoding="utf-8")
    return {
        match.group(1): match.group(2).lower()
        for match in re.finditer(
            r'^\s*([A-Za-z_][\w]*)\s*=\s*"([0-9a-fA-F]{6})"\s*,?\s*$',
            text,
            re.MULTILINE,
        )
    }


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


def cava_colours(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    section = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section != "color":
            continue
        match = re.match(r"([\w-]+)\s*=\s*'#?([0-9a-fA-F]{6})'", line)
        if match:
            values[match.group(1)] = match.group(2).lower()
    return values


def fuzzel_colours(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    section = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section != "colors" or not line or line.startswith("#"):
            continue
        match = re.match(r"([\w-]+)\s*=\s*([0-9a-fA-F]{8})", line)
        if match:
            values[match.group(1)] = match.group(2).lower()
    return values


def btop_colours(path: Path) -> dict[str, str]:
    return {
        match.group(1): match.group(2).lower()
        for match in re.finditer(
            r"^theme\[([^\]]+)\]\s*=\s*#([0-9a-fA-F]{6})",
            path.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    }


def spicetify_colours(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    section = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1]
            continue
        if section != "caelestia":
            continue
        match = re.match(r"([\w-]+)\s*=\s*([0-9a-fA-F]{6})\b", stripped)
        if match:
            values[match.group(1)] = match.group(2).lower()
    return values


def micro_links(path: Path) -> dict[str, str]:
    return {
        match.group(1): match.group(2)
        for match in re.finditer(
            r'^color-link\s+(\S+)\s+"([^"]*)"',
            path.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    }


def check_regular(path: Path, label: str) -> None:
    report(path.is_file() and not path.is_symlink(), f"{label} is a tracked regular file", str(path))


def check_colours(path: Path, label: str, actual: dict[str, str], expected: dict[str, str]) -> None:
    missing = sorted(set(expected) - set(actual))
    report(not missing, f"{label} defines every palette key", ", ".join(missing))
    wrong = [
        f"{key}={actual.get(key, '<missing>')} (want {value})"
        for key, value in expected.items()
        if actual.get(key) != value
    ]
    report(not wrong, f"{label} values match hypr/scheme/current.lua", "; ".join(wrong[:8]))


def main() -> int:
    print("app theme fallback contract")
    palette = load_palette()
    report(bool(palette), "hypr/scheme/current.lua parses", str(PALETTE))
    report(
        palette.get("surface") in {"131318", "f8fbf1"},
        "current palette is a tracked Machinedramon scheme",
        str(palette.get("surface")),
    )

    required_roles = {
        "surface", "onSurface", "primary", "onPrimary", "primaryContainer",
        "onPrimaryContainer", "onSurfaceVariant", "tertiary", "outline",
        "outlineVariant", "surfaceContainer", "surfaceContainerHigh",
        "surfaceContainerHighest", "secondary", "secondaryContainer",
        "error", "onError", "errorContainer", "shadow", "green", "teal",
        "sky", "sapphire", "blue", "lavender", "mauve", "maroon", "peach",
        "yellow", "red",
    }
    absent_roles = sorted(required_roles - set(palette))
    report(not absent_roles, "current palette has every role used by the fallbacks", ", ".join(absent_roles))

    if not palette:
        print(f"\n{failures} app theme check(s) failed ({checks} run)")
        return 1

    # cava
    check_regular(CAVA, "cava/config")
    cava = cava_colours(CAVA)
    cava_expected = {
        "background": palette["surface"],
        "foreground": palette["onSurface"],
        "gradient_color_1": palette["green"],
        "gradient_color_2": palette["teal"],
        "gradient_color_3": palette["sky"],
        "gradient_color_4": palette["sapphire"],
        "gradient_color_5": palette["blue"],
        "gradient_color_6": palette["lavender"],
        "gradient_color_7": palette["mauve"],
        "gradient_color_8": palette["maroon"],
    }
    check_colours(CAVA, "cava/config", cava, cava_expected)

    # fuzzel
    check_regular(FUZZEL, "fuzzel/fuzzel.ini")
    fuzzel = fuzzel_colours(FUZZEL)
    fuzzel_roles = {
        "background": "surface",
        "text": "onSurface",
        "prompt": "primary",
        "placeholder": "outline",
        "input": "onSurface",
        "match": "tertiary",
        "selection": "primaryContainer",
        "selection-text": "onPrimaryContainer",
        "selection-match": "tertiary",
        "counter": "outline",
        "border": "outline",
    }
    fuzzel_expected = {key: palette[role] + "ff" for key, role in fuzzel_roles.items()}
    check_colours(FUZZEL, "fuzzel/fuzzel.ini", fuzzel, fuzzel_expected)
    report(
        all(re.fullmatch(r"[0-9a-f]{8}", value) for value in fuzzel.values()),
        "fuzzel/fuzzel.ini colours are opaque rrggbbaa values",
    )

    # btop
    check_regular(BTOP, "btop/themes/caelestia.theme")
    btop = btop_colours(BTOP)
    btop_roles = {
        "main_bg": "surface",
        "main_fg": "onSurface",
        "title": "onSurface",
        "hi_fg": "primary",
        "selected_bg": "primaryContainer",
        "selected_fg": "onPrimaryContainer",
        "inactive_fg": "outline",
        "graph_text": "tertiary",
        "meter_bg": "surfaceContainerHighest",
        "proc_misc": "tertiary",
        "cpu_box": "mauve",
        "mem_box": "green",
        "net_box": "maroon",
        "proc_box": "blue",
        "div_line": "outline",
        "temp_start": "green",
        "temp_mid": "yellow",
        "temp_end": "red",
        "cpu_start": "teal",
        "cpu_mid": "sapphire",
        "cpu_end": "lavender",
        "free_start": "mauve",
        "free_mid": "lavender",
        "free_end": "blue",
        "cached_start": "sapphire",
        "cached_mid": "blue",
        "cached_end": "lavender",
        "available_start": "peach",
        "available_mid": "maroon",
        "available_end": "red",
        "used_start": "green",
        "used_mid": "teal",
        "used_end": "sky",
        "download_start": "peach",
        "download_mid": "maroon",
        "download_end": "red",
        "upload_start": "green",
        "upload_mid": "teal",
        "upload_end": "sky",
        "process_start": "sapphire",
        "process_mid": "lavender",
        "process_end": "mauve",
    }
    btop_expected = {key: palette[role] for key, role in btop_roles.items()}
    check_colours(BTOP, "btop/themes/caelestia.theme", btop, btop_expected)

    # Spicetify
    check_regular(SPICE_CONFIG, "spicetify/config-xpui.ini")
    check_regular(SPICE_COLOURS, "spicetify/Themes/caelestia/color.ini")
    spice_config = read_ini(SPICE_CONFIG)
    if spice_config is not None:
        report(spice_config.has_section("Setting"), "spicetify/config-xpui.ini has [Setting]")
        if spice_config.has_section("Setting"):
            setting = spice_config["Setting"]
            report(setting.get("current_theme") == "caelestia", "Spicetify selects the caelestia theme")
            report(setting.get("color_scheme") == "caelestia", "Spicetify selects the caelestia colour scheme")
            report(setting.get("inject_css") == "1", "Spicetify injects the theme CSS")
            report(setting.get("inject_theme_js") == "1", "Spicetify injects the theme JavaScript")
            report(setting.get("replace_colors") == "1", "Spicetify replaces the client colours")
            report(setting.get("overwrite_assets") == "0", "Spicetify does not overwrite client assets")

    spice = spicetify_colours(SPICE_COLOURS)
    spice_roles = {
        "text": "onSurface",
        "subtext": "onSurfaceVariant",
        "main": "surfaceContainer",
        "highlight": "primaryContainer",
        "misc": "onSurfaceVariant",
        "notification": "surfaceContainerHigh",
        "notification-error": "errorContainer",
        "shadow": "shadow",
        "card": "surfaceContainerHigh",
        "player": "secondaryContainer",
        "sidebar": "surface",
        "main-elevated": "surfaceContainerHigh",
        "highlight-elevated": "surfaceContainerHighest",
        "selected-row": "onSurface",
        "equalizer": "secondary",
        "button": "primary",
        "button-active": "primary",
        "button-disabled": "outline",
        "tab-active": "surfaceContainerHigh",
        "accent": "primary",
    }
    # The light template moves four surfaces so a light palette keeps its
    # contrast; infer the mode from the tracked surface instead of assuming it.
    channels = [int(palette["surface"][i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        for c in channels
    ]
    if 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2] > 0.5:
        spice_roles.update({
            "main": "surface",
            "card": "surfaceContainer",
            "sidebar": "surfaceContainer",
            "tab-active": "surfaceContainer",
        })
    spice_expected = {key: palette[role] for key, role in spice_roles.items()}
    check_colours(SPICE_COLOURS, "spicetify/Themes/caelestia/color.ini", spice, spice_expected)

    # micro
    check_regular(MICRO, "micro/colorschemes/padilha.micro")
    micro = micro_links(MICRO)
    micro_expected = {
        "default": f'#{palette["onSurface"]},#{palette["surface"]}',
        "comment": f'#{palette["onSurfaceVariant"]}',
        "constant": f'#{palette["maroon"]}',
        "constant.string": f'#{palette["green"]}',
        "statement": f'#{palette["primary"]}',
        "type": f'#{palette["blue"]}',
        "error": f'bold #{palette["onError"]},#{palette["error"]}',
        "selection": f'#{palette["onSurface"]},#{palette["primaryContainer"]}',
        "statusline": f'#{palette["onSurface"]},#{palette["surfaceContainerHigh"]}',
        "tabbar": f'#{palette["onSurfaceVariant"]},#{palette["surfaceContainer"]}',
        "current-line-number": f'bold #{palette["primary"]}',
        "match-brace": f'bold #{palette["onPrimary"]},#{palette["primary"]}',
    }
    check_colours(MICRO, "micro/colorschemes/padilha.micro", micro, micro_expected)
    report(
        micro.get("default", "").startswith("#" + palette["onSurface"] + ","),
        "micro fallback is the current scheme, not the old light palette",
        str(micro.get("default")),
    )

    # GTK settings
    gtk3 = read_ini(GTK3)
    gtk4 = read_ini(GTK4)
    if gtk3 is not None and gtk4 is not None:
        report(gtk3.has_section("Settings"), "gtk-3.0/settings.ini has [Settings]")
        report(gtk4.has_section("Settings"), "gtk-4.0/settings.ini has [Settings]")
        if gtk3.has_section("Settings") and gtk4.has_section("Settings"):
            report(
                dict(gtk3["Settings"]) == dict(gtk4["Settings"]),
                "GTK 3 and GTK 4 settings select the same base theme",
            )
            report(
                gtk3["Settings"].get("gtk-theme-name") == "adw-gtk3-dark",
                "GTK settings select adw-gtk3-dark",
            )
            report(
                gtk3["Settings"].get("gtk-icon-theme-name") == "Papirus-Dark",
                "GTK settings select Papirus-Dark",
            )
    for directory in (ROOT / "gtk-3.0", ROOT / "gtk-4.0"):
        for filename in ("gtk.css", "thunar.css"):
            generated = directory / filename
            report(
                not generated.exists(),
                f"{generated.relative_to(ROOT)} stays out of the checkout",
            )

    # Documentation must stay in sync with the contract.
    for path, label in ((COVERAGE, "coverage"), (FOLLOW_UP, "follow-up"), (VISUAL, "visual checklist")):
        report(path.is_file(), f"{path.relative_to(ROOT)} exists")
        if path.is_file():
            report("{{" not in path.read_text(encoding="utf-8"), f"{label} has no template placeholders")
    if COVERAGE.is_file():
        text = COVERAGE.read_text(encoding="utf-8")
        lower = text.lower()
        for app in (
            "Firefox", "Thunar", "GTK / Flatpak", "btop", "cava", "fuzzel",
            "micro", "Midnight Commander", "Spotify / Spicetify", "Discord",
        ):
            report(app.lower() in lower, f"coverage table names {app}")
        for status in ("Themed", "Partially themed", "Impossible"):
            report(status.lower() in lower, f"coverage table defines {status}")
        report("share/templates/" in text, "coverage table names the generator templates")
    if FOLLOW_UP.is_file():
        text = FOLLOW_UP.read_text(encoding="utf-8")
        report("maria-padilha-de" in text, "follow-up names maria-padilha-de")
        report("discord.scss" in text, "follow-up names the Discord template")
        report("caelestia.theme.css" in text, "follow-up names the generated Discord theme")
        report("@import" in text, "follow-up records the stale remote import")
        report("~/.var/app" in text, "follow-up records the Flatpak boundary")
    if VISUAL.is_file():
        text = VISUAL.read_text(encoding="utf-8")
        for app in ("Firefox", "Thunar", "Flatpak", "btop", "cava", "fuzzel", "micro", "Midnight Commander", "Spicetify", "Discord"):
            report(app.lower() in text.lower(), f"visual checklist covers {app}")

    if failures:
        print(f"\n{failures} app theme check(s) failed ({checks} run)")
        return 1
    print(f"\n{checks} app theme checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
