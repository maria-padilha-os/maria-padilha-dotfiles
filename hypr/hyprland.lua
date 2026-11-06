local home   = os.getenv("HOME")
local hypr   = home .. "/.config/hypr"

-- User config lives in ~/.config/padilha. The pre-rename ~/.config/lilith is
-- read instead only while the padilha directory does not exist.
--
-- PADILHA_CONFIG_DIR / LILITH_CONFIG_DIR name a directory. The older
-- PADILHA_CONFIG / LILITH_CONFIG variables are shared with the shell, whose
-- session exports the *compiler executable* under that name; only accept them
-- here when they really point at a directory.
local xdg_config = os.getenv("XDG_CONFIG_HOME") or (home .. "/.config")

local function quote(s)
    return "'" .. tostring(s):gsub("'", "'\\''") .. "'"
end

local function is_dir(path)
    if path == nil or path == "" then
        return false
    end
    -- io.popen is already used elsewhere in this config; os.execute return
    -- conventions differ between Lua builds, so keep the check explicit.
    local ok, handle = pcall(io.popen, "test -d " .. quote(path) .. " && printf yes")
    if not ok or not handle then
        return false
    end
    local out = handle:read("*l")
    handle:close()
    return out == "yes"
end

local function config_home(name, legacy_name)
    local explicit = os.getenv(name)
    if is_dir(explicit) then
        return explicit
    end
    local legacy = os.getenv(legacy_name)
    if is_dir(legacy) then
        return legacy
    end
    return nil
end

local config_dir = config_home("PADILHA_CONFIG_DIR", "PADILHA_CONFIG")
    or (xdg_config .. "/padilha")
local legacy_config_dir = config_home("LILITH_CONFIG_DIR", "LILITH_CONFIG")
    or (xdg_config .. "/lilith")

local function exists(path)
    local f = io.open(path, "r")
    if f then
        f:close()
        return true
    end
    return false
end

local config_root = config_dir
if not exists(config_dir) and exists(legacy_config_dir) then
    config_root = legacy_config_dir
end

package.path = package.path .. ";" .. config_root .. "/?.lua"

-- Every user file is read from the selected config root; a missing one is
-- created there by maybe_create.
local function user_file(name)
    return config_root .. "/" .. name
end

-- Create a file if it doesn't exist, optionally with initial content
local function maybe_create(file, content)
    local f = io.open(file)

    if f then
        f:close()
        return true
    end

    f = io.open(file, "w")
    if not f then return false end

    if content then f:write(content) end
    f:close()
    return true
end

-- Copy src to dst, but only if dst doesn't already exist
local function maybe_copy(src, dst)
    local out = io.open(dst)
    if out then
        out:close()
        return
    end

    local input = io.open(src, "r")
    if not input then return end

    out = io.open(dst, "w")
    if out then
        out:write(input:read("*a"))
        out:close()
    end
    input:close()
end

-- Maybe set current colours to defaults
maybe_copy(hypr .. "/scheme/default.lua", hypr .. "/scheme/current.lua")

-- User variables
local overrides = maybe_create(
    user_file("hypr-vars.lua"),
    "return {}\n"
) and require("hypr-vars") or {}

if type(overrides) == "table" then
    local vars = require("variables")
    for k, v in pairs(overrides) do
        vars[k] = v
    end
end

-- Default monitor conf
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = 1,
})

-- Monitor rules written by the settings app. The default above only applies
-- when this file is empty, so a saved layout wins on the next reload.
local monitors_file = user_file("monitors.lua")
if maybe_create(monitors_file, "return {}\n") then
    local ok, rules = pcall(dofile, monitors_file)
    if ok and type(rules) == "table" then
        for _, rule in ipairs(rules) do
            if type(rule) == "table" and rule.output then
                hl.monitor(rule)
            end
        end
    end
end

-- Configs
require("hyprland.env")
require("hyprland.general")
require("hyprland.input")
require("hyprland.misc")
require("hyprland.animations")
require("hyprland.decoration")
require("hyprland.group")
require("hyprland.execs")
require("hyprland.rules")
require("hyprland.gestures")
require("hyprland.keybinds")

-- User configs
if maybe_create(user_file("hypr-user.lua")) then
    require("hypr-user")
end
