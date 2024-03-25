ardour {
	["type"] = "EditorAction",
	name = "Tempo - Estimate Tempo",
	author      = "Justin Ehrlichman",
description = [[
Estimate the tempo of a selected audio region and set tempo markers
]]
}

function factory () return function (signal, ...)




local sel = Editor:get_selection()
local count = 0
local midi_region

for r in sel.regions:regionlist():iter() do
    count = count + 1
    if r:to_audioregion():isnil() then
       local md = LuaDialog.Message ("Estimate Tempo", "The selected region is not an audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
	print (md:run())
         md = nil
	collectgarbage ()
        return
    else
        audio_region = r
    end
end

if count ~= 1 then
       local md = LuaDialog.Message ("Esitmate Tempo", "Please select exactly 1 audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
	print (md:run())
         md = nil
	collectgarbage ()
    return
end

local rn = audio_region:name()
local source = audio_region:source(0):to_filesource():path()
print(source)
local filepath = source


local quotedfilepath = '"' .. filepath .. '"'

local command = "bpmbin  " ..quotedfilepath


os.execute(command)

local handle = io.popen(command)
local result = handle:read("*a")
handle:close()

local md = LuaDialog.Message("Estimate Tempo", result, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
print(md:run())
md = nil
collectgarbage()

-- to do, add tempo markers and prompt whether or not you want to tempo markers




end end

















