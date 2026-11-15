#!/usr/bin/env bash
# Keymap contract checks for nvim/lua/mappings.lua. This parses the Lua source
# with the plain `lua` interpreter that CI already installs; it never starts
# Neovim, a shell, or a terminal.
set -uo pipefail

root=$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
mappings=${1:-"$root/nvim/lua/mappings.lua"}

if ! command -v lua >/dev/null 2>&1; then
    printf 'keymaps: lua is required\n' >&2
    exit 2
fi

exec lua - "$mappings" <<'LUA'
local path = arg[1]
local file, err = io.open(path, "rb")
if not file then
    io.stderr:write(("keymaps: cannot read %s: %s\n"):format(path, err))
    os.exit(2)
end
local source = file:read("*a")
file:close()

local pass, fail = 0, 0
local function ok(name) pass = pass + 1; print(("  ok   %s"):format(name)) end
local function bad(name, detail)
    fail = fail + 1
    print(("  FAIL %s"):format(name))
    if detail and detail ~= "" then print(("       %s"):format(detail)) end
end

local function trim(value)
    return (value:gsub("^%s+", ""):gsub("%s+$", ""))
end

-- Drop -- comments while preserving strings and newlines, so a commented-out
-- mapping can never satisfy (or break) a check.
local function strip_comments(text)
    local out, i, quote = {}, 1, nil
    while i <= #text do
        local char = text:sub(i, i)
        if quote then
            out[#out + 1] = char
            if char == "\\" then
                out[#out + 1] = text:sub(i + 1, i + 1)
                i = i + 2
            else
                if char == quote then quote = nil end
                i = i + 1
            end
        elseif char == '"' or char == "'" then
            quote = char
            out[#out + 1] = char
            i = i + 1
        elseif char == "-" and text:sub(i + 1, i + 1) == "-" then
            while i <= #text and text:sub(i, i) ~= "\n" do i = i + 1 end
        else
            out[#out + 1] = char
            i = i + 1
        end
    end
    return table.concat(out)
end

local clean = strip_comments(source)

local function line_at(position)
    local _, newlines = clean:sub(1, position):gsub("\n", "\n")
    return newlines + 1
end

local function next_nonspace(position)
    while position <= #clean and clean:sub(position, position):match("%s") do
        position = position + 1
    end
    return position
end

local function find_close(open)
    local depth, i, quote = 0, open, nil
    while i <= #clean do
        local char = clean:sub(i, i)
        if quote then
            if char == "\\" then
                i = i + 2
            else
                if char == quote then quote = nil end
                i = i + 1
            end
        elseif char == '"' or char == "'" then
            quote = char
            i = i + 1
        elseif char == "(" then
            depth = depth + 1
            i = i + 1
        elseif char == ")" then
            depth = depth - 1
            if depth == 0 then return i end
            i = i + 1
        else
            i = i + 1
        end
    end
end

local function split_args(body)
    local args, start, i = {}, 1, 1
    local parens, braces, brackets, quote = 0, 0, 0, nil
    while i <= #body do
        local char = body:sub(i, i)
        if quote then
            if char == "\\" then
                i = i + 2
            else
                if char == quote then quote = nil end
                i = i + 1
            end
        elseif char == '"' or char == "'" then
            quote = char
            i = i + 1
        elseif char == "(" then
            parens = parens + 1
            i = i + 1
        elseif char == ")" then
            parens = parens - 1
            i = i + 1
        elseif char == "{" then
            braces = braces + 1
            i = i + 1
        elseif char == "}" then
            braces = braces - 1
            i = i + 1
        elseif char == "[" then
            brackets = brackets + 1
            i = i + 1
        elseif char == "]" then
            brackets = brackets - 1
            i = i + 1
        elseif char == "," and parens == 0 and braces == 0 and brackets == 0 then
            args[#args + 1] = body:sub(start, i - 1)
            start = i + 1
            i = i + 1
        else
            i = i + 1
        end
    end
    args[#args + 1] = body:sub(start)
    return args
end

local function string_value(value)
    local text = trim(value)
    local quote = text:sub(1, 1)
    if (quote == '"' or quote == "'") and #text >= 2 and text:sub(-1) == quote then
        return text:sub(2, -2)
    end
end

local function parse_modes(value)
    local text = trim(value)
    local modes = {}
    if text:sub(1, 1) == "{" and text:sub(-1) == "}" then
        local inner = text:sub(2, -2)
        for piece in inner:gmatch("[^,]+") do
            local mode = string_value(piece)
            if not mode then return nil end
            modes[#modes + 1] = mode
        end
        return modes
    end
    local mode = string_value(text)
    if mode then return { mode } end
    return nil
end

local maps, parse_errors = {}, {}

local function parse_calls(name)
    local position = 1
    while true do
        local start, finish = clean:find(name, position, true)
        if not start then break end
        position = finish + 1

        local before = start > 1 and clean:sub(start - 1, start - 1) or ""
        local after = clean:sub(finish + 1, finish + 1)
        local is_word = function(char) return char ~= "" and char:match("[%w_]") ~= nil end
        if not is_word(before) and not is_word(after) then
            local open = next_nonspace(finish + 1)
            if clean:sub(open, open) == "(" then
                local close = find_close(open)
                if not close then
                    parse_errors[#parse_errors + 1] = ("line %d: unterminated %s()"):format(line_at(start), name)
                else
                    local args = split_args(clean:sub(open + 1, close - 1))
                    local modes = args[1] and parse_modes(args[1])
                    local lhs = args[2] and string_value(args[2])
                    if not modes or not lhs then
                        parse_errors[#parse_errors + 1] = ("line %d: could not parse %s() modes/lhs"):format(line_at(start), name)
                    else
                        local rhs = trim(args[3] or "")
                        local opts = args[4] or ""
                        local desc = opts:match('desc%s*=%s*"([^"]*)"')
                            or opts:match("desc%s*=%s*'([^']*)'")
                        maps[#maps + 1] = {
                            modes = modes,
                            lhs = lhs,
                            rhs = rhs,
                            desc = desc,
                            line = line_at(start),
                        }
                    end
                end
            end
        end
    end
end

parse_calls("map")
parse_calls("vim.keymap.set")

if #parse_errors == 0 then
    ok(("all keymap calls parsed (%d found)"):format(#maps))
else
    bad("all keymap calls parsed", table.concat(parse_errors, "; "))
end

local function has_mode(mapping, wanted)
    for _, mode in ipairs(mapping.modes) do
        if mode == wanted then return true end
    end
    return false
end

local function mapping_label(mapping)
    return ("line %d: %s -> %s"):format(mapping.line, mapping.lhs, mapping.rhs)
end

local function check_normal_key_unbound(key)
    local offenders = {}
    for _, mapping in ipairs(maps) do
        if has_mode(mapping, "n") and mapping.lhs:upper() == key:upper() then
            offenders[#offenders + 1] = mapping_label(mapping)
        end
    end
    local name = ("normal mode leaves %s unbound"):format(key)
    if #offenders == 0 then
        ok(name)
    else
        bad(name, table.concat(offenders, "; "))
    end
end

check_normal_key_unbound("<BS>")
check_normal_key_unbound("<A-BS>")

local function check_defold(description, key, argument)
    local found = {}
    for _, mapping in ipairs(maps) do
        if mapping.desc == description then found[#found + 1] = mapping end
    end

    local name = ("%s is on %s"):format(description, key)
    if #found ~= 1 then
        bad(name, ("expected one %q mapping, found %d"):format(description, #found))
        return
    end

    local mapping = found[1]
    local problems = {}
    if not has_mode(mapping, "n") then problems[#problems + 1] = "not in normal mode" end
    if mapping.lhs:upper() ~= key:upper() then problems[#problems + 1] = "wrong key" end
    if not mapping.rhs:find("mterm", 1, true) then problems[#problems + 1] = "does not use mterm()" end
    if not mapping.rhs:find("defold", 1, true) then problems[#problems + 1] = "does not invoke defold" end
    if argument == "" then
        if mapping.rhs:find("--no-build", 1, true) then problems[#problems + 1] = "build mapping has --no-build" end
    elseif not mapping.rhs:find(argument, 1, true) then
        problems[#problems + 1] = "relaunch mapping is missing " .. argument
    end

    if #problems == 0 then
        ok(name)
    else
        bad(name, ("line %d: %s"):format(mapping.line, table.concat(problems, "; ")))
    end
end

check_defold("defold build & run", "<F5>", "")
check_defold("defold relaunch", "<F6>", "--no-build")

local terminal_launchers = {}
for _, mapping in ipairs(maps) do
    if mapping.rhs:match("mterm%s*%(") or mapping.rhs:match("term%.toggle") then
        terminal_launchers[#terminal_launchers + 1] = mapping
    end
end

if #terminal_launchers == 0 then
    bad("terminal launchers were found", "no mterm()/term.toggle() mapping parsed")
else
    ok(("terminal launchers were found (%d checked)"):format(#terminal_launchers))
end

local editing_keys = {
    ["<BS>"] = true, ["<A-BS>"] = true, ["<C-BS>"] = true, ["<S-BS>"] = true,
    ["<DEL>"] = true, ["<A-DEL>"] = true, ["<C-DEL>"] = true,
    ["<CR>"] = true, ["<ENTER>"] = true, ["<SPACE>"] = true, ["<TAB>"] = true,
    ["<ESC>"] = true,
    ["<UP>"] = true, ["<DOWN>"] = true, ["<LEFT>"] = true, ["<RIGHT>"] = true,
    ["<HOME>"] = true, ["<END>"] = true, ["<PAGEUP>"] = true, ["<PAGEDOWN>"] = true,
    ["<INSERT>"] = true, ["<C-H>"] = true, ["<C-W>"] = true, ["<C-U>"] = true,
}

local function is_editing_key(lhs)
    if editing_keys[lhs:upper()] then return true end
    -- A bare printable character is a normal/insert editing key too.
    return #lhs == 1 and lhs:match("%g") ~= nil
end

local mode_problems, shape_problems, description_problems, editing_problems = {}, {}, {}, {}
for _, mapping in ipairs(terminal_launchers) do
    local label = ("line %d: %s"):format(mapping.line, mapping.lhs)

    if #mapping.modes == 0 or mapping.lhs == "" or mapping.lhs == "*" then
        shape_problems[#shape_problems + 1] = label .. " has an empty/wildcard mode or key"
    end
    for _, mode in ipairs(mapping.modes) do
        if mode == "" or mode == "*" then
            mode_problems[#mode_problems + 1] = label .. " has an empty/wildcard mode"
        end
    end
    if not mapping.desc or mapping.desc == "" then
        description_problems[#description_problems + 1] = label .. " has no desc"
    end
    if is_editing_key(mapping.lhs) then
        editing_problems[#editing_problems + 1] = label .. " swallows an editing key"
    end
end

local function joined(...)
    local out = {}
    for _, list in ipairs({ ... }) do
        for _, item in ipairs(list) do out[#out + 1] = item end
    end
    return table.concat(out, "; ")
end

if #mode_problems == 0 and #shape_problems == 0 then
    ok("terminal launchers use explicit modes and keys")
else
    bad("terminal launchers use explicit modes and keys", joined(mode_problems, shape_problems))
end

if #description_problems == 0 then
    ok("terminal launchers have an explicit description")
else
    bad("terminal launchers have an explicit description", table.concat(description_problems, "; "))
end

if #editing_problems == 0 then
    ok("terminal launchers avoid normal editing keys")
else
    bad("terminal launchers avoid normal editing keys", table.concat(editing_problems, "; "))
end

print(("\n%d passed, %d failed\n"):format(pass, fail))
os.exit(fail == 0 and 0 or 1)
LUA
