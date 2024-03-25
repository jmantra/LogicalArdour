ardour {
	["type"] = "EditorAction",
	name = "Tempo - Estimate Tempo",
	author      = "Justin Ehrlichman",
description = [[
Estimate the tempo of a selected audio region and tempo markers
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






local md = LuaDialog.Message ("Estimate Tempo", "The path is " .. filepath, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
print(md:run())

md = nil
collectgarbage()

end end











e






