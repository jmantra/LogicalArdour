ardour {
	["type"] = "EditorAction",
	name = "Key - Get the key of an audio loop",
	author      = "Justin Ehrlichman",
description = [[
Estimates the key of an audio loop for the purpose of autotune
]]
}

function factory () return function (signal, ...)




local sel = Editor:get_selection()
local count = 0
local midi_region

for r in sel.regions:regionlist():iter() do
    count = count + 1
    if r:to_audioregion():isnil() then
        local md = LuaDialog.Message("Get Key", "The selected region is not an audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
        print(md:run())
        md = nil
        collectgarbage()
        return
    else
        audio_region = r
    end
end

if count ~= 1 then
    local md = LuaDialog.Message("Get Key", "Please select exactly 1 audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
    print(md:run())
    md = nil
    collectgarbage()
    return
end

local rn = audio_region:name()
local source = audio_region:source(0):to_filesource():path()
print(source)
local filepath = source


local quotedfilepath = '"' .. filepath .. '"'


-- Example usage:
local filename = quotedfilepath



    -- local command = "sox  " ..quotedfilepath.. " -t raw -r 48000  -e float -c 1 - | bpm"



  local command = "key " .. quotedfilepath

os.execute(command)


-- Open the file in write mode



   local handle = io.popen(command)
    local firstresult = handle:read("*a")
    handle:close()

    print(firstresult)


     local md = LuaDialog.Message("Estimate Tempo", firstresult, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
    print(md:run())
    md = nil
    collectgarbage()




















end end

















