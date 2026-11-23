#!/usr/bin/env python3
"""Static and installer contract checks for the GTK and Flatpak theme files.

Nothing here launches an application, talks to Flatpak or needs a display. The
static checks parse the tracked settings and override files; the installer
checks exercise ``bin/padilha-dots`` against a scratch HOME and XDG directories.
"""

from __future__ import annotations

import configparser
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOTS = ROOT / "bin" / "padilha-dots"
GTK_DIRS = (ROOT / "gtk-3.0", ROOT / "gtk-4.0")
FLATPAK_OVERRIDE = ROOT / "flatpak" / "overrides" / "global"

EXPECTED_THEME = "adw-gtk3-dark"
EXPECTED_ICON = "Papirus-Dark"
EXPECTED_FONT = "Noto Sans 10"
GENERATED_CSS = ("gtk.css", "thunar.css")

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


def read_ini(path: Path) -> configparser.ConfigParser | None:
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str
    try:
        with path.open(encoding="utf-8") as handle:
            parser.read_file(handle)
    except (OSError, configparser.Error) as error:
        report(False, f"{path.relative_to(ROOT)} parses", str(error))
        return None
    return parser


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False
    return None


def check_settings() -> None:
    values_by_version: dict[str, configparser.SectionProxy] = {}

    for directory in GTK_DIRS:
        path = directory / "settings.ini"
        name = path.relative_to(ROOT)
        if not path.is_file():
            report(False, f"{name} exists")
            continue
        report(True, f"{name} exists")

        config = read_ini(path)
        if config is None:
            continue
        report(config.has_section("Settings"), f"{name} has [Settings]")
        if not config.has_section("Settings"):
            continue

        values = config["Settings"]
        values_by_version[directory.name] = values
        report(
            values.get("gtk-theme-name", "").strip() == EXPECTED_THEME,
            f"{name} selects {EXPECTED_THEME}",
            str(values.get("gtk-theme-name")),
        )
        report(
            values.get("gtk-icon-theme-name", "").strip() == EXPECTED_ICON,
            f"{name} selects {EXPECTED_ICON} icons",
            str(values.get("gtk-icon-theme-name")),
        )
        report(
            values.get("gtk-font-name", "").strip() == EXPECTED_FONT,
            f"{name} selects {EXPECTED_FONT}",
            str(values.get("gtk-font-name")),
        )
        report(
            parse_bool(values.get("gtk-application-prefer-dark-theme")) is True,
            f"{name} asks for the dark preference",
            str(values.get("gtk-application-prefer-dark-theme")),
        )

        for filename in GENERATED_CSS:
            generated = directory / filename
            report(
                not generated.exists(),
                f"{generated.relative_to(ROOT)} stays out of the checkout",
            )

    if len(values_by_version) == 2:
        gtk3 = values_by_version["gtk-3.0"]
        gtk4 = values_by_version["gtk-4.0"]
        report(
            gtk3.get("gtk-theme-name") == gtk4.get("gtk-theme-name"),
            "GTK 3 and GTK 4 select the same theme",
        )
        report(
            gtk3.get("gtk-icon-theme-name") == gtk4.get("gtk-icon-theme-name"),
            "GTK 3 and GTK 4 select the same icon theme",
        )
        report(
            gtk3.get("gtk-font-name") == gtk4.get("gtk-font-name"),
            "GTK 3 and GTK 4 select the same font",
        )

    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for generated in (
        "gtk-3.0/gtk.css",
        "gtk-3.0/thunar.css",
        "gtk-4.0/gtk.css",
        "gtk-4.0/thunar.css",
    ):
        report(generated in ignore, f".gitignore ignores generated {generated}")


def check_flatpak_override() -> None:
    name = "flatpak/overrides/global"
    if not FLATPAK_OVERRIDE.is_file():
        report(False, f"{name} exists")
        return
    report(True, f"{name} exists")

    config = read_ini(FLATPAK_OVERRIDE)
    if config is None:
        return

    report(config.has_section("Context"), f"{name} has [Context]")
    report(config.has_section("Environment"), f"{name} has [Environment]")

    if config.has_section("Context"):
        filesystems = config["Context"].get("filesystems", "")
        report(
            "/usr/share/themes:ro" in filesystems,
            f"{name} exposes the host themes read-only",
            filesystems,
        )
        report(
            "/usr/share/icons:ro" in filesystems,
            f"{name} exposes the host icons read-only",
            filesystems,
        )
        for version in ("gtk-3.0", "gtk-4.0"):
            report(
                f"xdg-config/{version}:ro" in filesystems,
                f"{name} exposes generated {version} CSS read-only",
                filesystems,
            )

    if config.has_section("Environment"):
        environment = config["Environment"]
        report(
            environment.get("GTK_THEME") == EXPECTED_THEME,
            f"{name} sets GTK_THEME={EXPECTED_THEME}",
            str(environment.get("GTK_THEME")),
        )
        report(
            environment.get("GTK_CSD") == "1",
            f"{name} keeps client-side decorations",
            str(environment.get("GTK_CSD")),
        )

    text = FLATPAK_OVERRIDE.read_text(encoding="utf-8")
    report("--system" not in text, f"{name} is not a system override")
    report("/var/lib/flatpak" not in text, f"{name} does not use the system installation")


def check_docs() -> None:
    docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "README.md",
            ROOT / "thunar" / "README.md",
            ROOT / "gtk-3.0" / "README.md",
            ROOT / "gtk-4.0" / "README.md",
            ROOT / "flatpak" / "README.md",
        )
    )
    lowered = docs.lower()

    for required in (
        "gtk-3.0/settings.ini",
        "gtk-4.0/settings.ini",
        "flatpak/overrides/global",
        "GTK_THEME",
        "libadwaita",
        "file chooser",
        "dialog",
        "menu",
        "ignore",
        "padilha-dots flatpak-reset",
        "flatpak override --user --reset",
        "user-scoped",
        "generated",
    ):
        report(required.lower() in lowered, f"README documents {required}")

    for generated in (
        "gtk-3.0/gtk.css",
        "gtk-3.0/thunar.css",
        "gtk-4.0/gtk.css",
        "gtk-4.0/thunar.css",
    ):
        report(generated in docs, f"README documents generated {generated}")
    report(
        "must not be edited" in lowered or "never edit" in lowered,
        "README says the generated CSS must not be edited",
    )


def run_dots(home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    config = home / ".config"
    data = home / ".local" / "share"
    env = os.environ.copy()
    env.update(
        HOME=str(home),
        XDG_CONFIG_HOME=str(config),
        XDG_DATA_HOME=str(data),
    )
    return subprocess.run(
        [str(DOTS), *args],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def link_to(path: Path, target: Path) -> bool:
    return path.is_symlink() and path.resolve() == target.resolve()


def check_installer() -> None:
    with tempfile.TemporaryDirectory(prefix="padilha-gtk-") as directory:
        home = Path(directory)
        config = home / ".config"
        data = home / ".local" / "share"
        for version in ("gtk-3.0", "gtk-4.0"):
            gtk_dir = config / version
            gtk_dir.mkdir(parents=True)
            for filename in GENERATED_CSS:
                (gtk_dir / filename).write_text(
                    f"/* {version}/{filename} sentinel */\n", encoding="utf-8"
                )

        result = run_dots(home, "gtk", "flatpak")
        report(
            result.returncode == 0,
            "padilha-dots gtk flatpak succeeds in a scratch HOME",
            result.stderr.strip(),
        )

        for version in ("gtk-3.0", "gtk-4.0"):
            destination = config / version / "settings.ini"
            source = ROOT / version / "settings.ini"
            report(
                link_to(destination, source),
                f"{version}/settings.ini links to the checkout",
                str(destination),
            )
            for filename in GENERATED_CSS:
                generated = config / version / filename
                report(
                    generated.is_file()
                    and not generated.is_symlink()
                    and generated.read_text(encoding="utf-8").startswith("/*")
                    and "sentinel" in generated.read_text(encoding="utf-8"),
                    f"installer keeps {version}/{filename} generated",
                )

        override = data / "flatpak" / "overrides" / "global"
        report(
            link_to(override, FLATPAK_OVERRIDE),
            "Flatpak override links into the user installation",
            str(override),
        )

        # Re-running must be idempotent and must still not touch generated CSS.
        result = run_dots(home, "gtk", "flatpak")
        report(
            result.returncode == 0,
            "the GTK and Flatpak targets are idempotent",
            result.stderr.strip(),
        )
        report(
            link_to(config / "gtk-4.0" / "settings.ini", ROOT / "gtk-4.0" / "settings.ini"),
            "rerunning keeps the GTK 4 settings link",
        )
        report(
            (config / "gtk-3.0" / "gtk.css").read_text(encoding="utf-8").endswith("sentinel */\n"),
            "rerunning keeps the generated GTK 3 CSS",
        )

        result = run_dots(home, "flatpak-reset")
        report(
            result.returncode == 0,
            "padilha-dots flatpak-reset succeeds",
            result.stderr.strip(),
        )
        report(not override.exists() and not override.is_symlink(), "flatpak-reset removes the link")
        report(
            link_to(config / "gtk-3.0" / "settings.ini", ROOT / "gtk-3.0" / "settings.ini"),
            "flatpak-reset leaves the GTK settings alone",
        )
        report(
            (config / "gtk-4.0" / "gtk.css").read_text(encoding="utf-8").endswith("sentinel */\n"),
            "flatpak-reset leaves generated CSS alone",
        )

        # A second reset is a no-op, and a real user override is never deleted.
        result = run_dots(home, "flatpak-reset")
        report(result.returncode == 0, "flatpak-reset is idempotent", result.stderr.strip())

    with tempfile.TemporaryDirectory(prefix="padilha-flatpak-") as directory:
        home = Path(directory)
        override = home / ".local" / "share" / "flatpak" / "overrides" / "global"
        override.parent.mkdir(parents=True)
        marker = "[Environment]\nUSER_SETTING=keep\n"
        override.write_text(marker, encoding="utf-8")

        result = run_dots(home, "flatpak")
        report(result.returncode == 0, "flatpak backs up a real user override", result.stderr.strip())
        backups = sorted(override.parent.glob("global.pre-padilha-*"))
        report(len(backups) == 1, "exactly one pre-padilha Flatpak backup is created")
        report(
            bool(backups) and backups[0].read_text(encoding="utf-8") == marker,
            "the real Flatpak override is preserved in the backup",
        )
        report(link_to(override, FLATPAK_OVERRIDE), "the managed Flatpak link replaces the real file")

        result = run_dots(home, "flatpak-reset")
        report(result.returncode == 0, "flatpak-reset works after a backup", result.stderr.strip())
        report(not override.exists(), "flatpak-reset removes the managed link")
        report(
            bool(backups) and backups[0].read_text(encoding="utf-8") == marker,
            "flatpak-reset keeps the preserved backup",
        )

    with tempfile.TemporaryDirectory(prefix="padilha-flatpak-real-") as directory:
        home = Path(directory)
        override = home / ".local" / "share" / "flatpak" / "overrides" / "global"
        override.parent.mkdir(parents=True)
        override.write_text("[Environment]\nUSER_SETTING=keep\n", encoding="utf-8")

        result = run_dots(home, "flatpak-reset")
        report(result.returncode == 0, "flatpak-reset accepts a real user override", result.stderr.strip())
        report(
            override.read_text(encoding="utf-8") == "[Environment]\nUSER_SETTING=keep\n",
            "flatpak-reset never deletes a real user override",
        )


def main() -> int:
    print("settings")
    check_settings()
    print("flatpak")
    check_flatpak_override()
    print("docs")
    check_docs()
    print("installer")
    check_installer()
    print(f"\n{checks} checks, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
