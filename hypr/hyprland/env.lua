local vars = require("variables")
local home = os.getenv("HOME")

-- Themes
hl.env("QT_QPA_PLATFORMTHEME", "qtengine")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
hl.env("XCURSOR_THEME", vars.cursorTheme)
hl.env("XCURSOR_SIZE", vars.cursorSize)

-- Toolkit backends
-- Compose dead keys (ABNT2: ' " ^ ~) in Qt apps. The Caelestia lock screen
-- feeds a real TextInput, so this is what turns dead-key sequences into á/ã.
hl.env("QT_IM_MODULE", "compose")
hl.env("GDK_BACKEND", "wayland,x11")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("SDL_VIDEODRIVER", "wayland,x11,windows")
hl.env("CLUTTER_BACKEND", "wayland")
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")

-- Default terminal, for apps and scripts that honour $TERMINAL.
hl.env("TERMINAL", vars.terminal)

-- XDG specifications
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")

-- Local secrets live in env.local.lua (gitignored).
-- Copy env.local.example.lua to env.local.lua and fill in your keys.
do
    local home = os.getenv("HOME")
    local path = home .. "/.config/hypr/hyprland/env.local.lua"
    local f = io.open(path, "r")
    if f then
        f:close()
        dofile(path)
    end
end

-- Others
hl.env("_JAVA_AWT_WM_NONREPARENTING", "1")

-- SSH agent socket, started by execs.lua (see hypr/utils/ssh-agent.sh). Set
-- here too so apps get it from the first spawn, not only after the script runs.
local runtime_dir = os.getenv("XDG_RUNTIME_DIR")
if runtime_dir then
    hl.env("SSH_AUTH_SOCK", runtime_dir .. "/ssh-agent.sock")
end

-- Maria Padilha shell: the checkout sits next to this dotfiles checkout, out
-- of ~/.config, and ~/.config/quickshell/caelestia symlinks into its shell/.
-- The C++ QML modules come from its build tree. The legacy lilith-de checkout
-- stays on the search path until the directory rename is complete.
local repos_root
do
    local ok, handle = pcall(io.popen,
        "readlink -f -- '" .. home .. "/.config/hypr' 2>/dev/null")
    if ok and handle then
        local config_dir = handle:read("*l")
        handle:close()
        local root = config_dir and config_dir:match("^(.*)/hypr$")
        if root then repos_root = root .. "/.." end
    end
end

if repos_root then
    local project = repos_root .. "/maria-padilha-de"
    local legacy_project = repos_root .. "/lilith-de"
    hl.env("QML2_IMPORT_PATH", project .. "/build/qml:" .. legacy_project .. "/build/qml")

    -- The project's own commands (padilha, padilha-shot, padilha-record, ...).
    -- Packaged installs put them in /usr/bin and this block can go.
    if os.getenv("PATH") then
        hl.env("PATH", project .. "/bin:" .. legacy_project .. "/bin:" .. os.getenv("PATH"))
    end
end
