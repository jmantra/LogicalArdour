ardour {
    ["type"] = "EditorHook",
    name = "MuseScore - Synchronize notes",
    license = "MIT",
    author = "Justin Ehrlichman",
    description = [[
Keep the open MuseScore score aligned with one MIDI region.

This hook does nothing unless the LogicalArdour sync plugin is running.
One MuseScore edit becomes one Ardour undo. Lyrics, slurs, and layout stay
in MuseScore.
]]
}

function signals()
    local set = LuaSignal.Set()
    if LuaSignal.LuaTimerDS ~= nil then
        set:add({ [LuaSignal.LuaTimerDS] = true })
    else
        set:add({ [LuaSignal.LuaTimerS] = true })
    end
    return set
end

function factory()
local function file_exists(path)
    if type(io) ~= "table" or type(io.open) ~= "function" then
        return false
    end
    local file = io.open(path, "rb")
    if file then
        file:close()
        return true
    end
    return false
end
local function run_file(path)
    if type(io) ~= "table" or type(io.open) ~= "function" then
        return false, "io is not available"
    end
    local handle = io.open(path, "r")
    if not handle then
        return false, "cannot open " .. path
    end
    local text = handle:read("*a")
    handle:close()
    local compiler = load
    if type(compiler) ~= "function" then
        compiler = loadstring
    end
    if type(compiler) ~= "function" then
        return false, "load is not available"
    end
    local chunk, err = compiler(text, "@" .. path)
    if not chunk then
        return false, err
    end
    return pcall(chunk)
end
local function load_common()
    local home = ""
    local xdg = ""
    if type(os) == "table" and type(os.getenv) == "function" then
        home = os.getenv("HOME") or ""
        xdg = os.getenv("XDG_CONFIG_HOME") or ""
    end
    local dirs = {}
    if xdg ~= "" then
        dirs[#dirs + 1] = xdg .. "/ardour9/scripts"
        dirs[#dirs + 1] = xdg .. "/ardour8/scripts"
    end
    dirs[#dirs + 1] = home .. "/.config/ardour9/scripts"
    dirs[#dirs + 1] = home .. "/.config/ardour8/scripts"
    dirs[#dirs + 1] = home .. "/.config/LogicalArdour/ardour9/scripts"
    dirs[#dirs + 1] = home .. "/.config/LogicalArdour/ardour8/scripts"
    for _, dir in ipairs(dirs) do
        local path = dir .. "/score_editor_common.lua"
        if file_exists(path) then
            ScoreEditor = ScoreEditor or {}
            ScoreEditor.script_dir = dir
            return run_file(path)
        end
    end
    return false
end

    local state = { ready = false }
    local common_ok = false

    return function()
        if not common_ok then
            common_ok = load_common()
        end
        if not common_ok or not ScoreEditor or not ScoreEditor.mscore_sync_tick then
            return
        end
        local ok, err = pcall(function()
            ScoreEditor.mscore_sync_tick(state)
        end)
        if not ok then
            print("MuseScore sync: " .. tostring(err))
        end
    end
end
