ardour {
    ["type"] = "EditorAction",
    name = "Musescore - Open Midi region in musical notation format",
    license = "MIT",
    author = "Justin Ehrlichman",
    description = [[
Open the selected MIDI region in MuseScore 3.

The score is imported once from the live MIDI region. Playback still uses
JACK. Note moves travel through Plugins → LogicalArdour sync.
]]
}

function factory()
local function file_exists(path)
    if type(io) ~= "table" or type(io.open) ~= "function" then
        return "no"
    end
    local file = io.open(path, "rb")
    if file then
        file:close()
        return "yes"
    end
    return "no"
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
    dirs[#dirs + 1] = "/usr/share/ardour9/scripts"
    dirs[#dirs + 1] = "/usr/share/ardour8/scripts"
    for _, dir in ipairs(dirs) do
        local path = dir .. "/score_editor_common.lua"
        if file_exists(path) == "yes" then
            ScoreEditor = ScoreEditor or {}
            ScoreEditor.script_dir = dir
            local ok, err = run_file(path)
            return ok, err
        end
    end
    return false, "score_editor_common.lua was not found"
end

return function()
    local common_ok, common_err = load_common()
    if not common_ok or not ScoreEditor or not ScoreEditor.open_in_musescore then
        print("MuseScore: " .. tostring(common_err))
        return
    end
    ScoreEditor.open_in_musescore()
end end
