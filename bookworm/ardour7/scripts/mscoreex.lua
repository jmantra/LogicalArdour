ardour {
	["type"] = "EditorAction",
	name = "Musescore - Open Midi region in musical notation format",
	author      = "Justin Ehrlichman",
description = [[
Takes a selected MIDI region, converts it to a PDF using musescore then opens up the PDF in Firefox
]]
}

function factory () return function (signal, ...)

local md = LuaDialog.Message ("Open Musical Score", "If Firefox shows a blank page, you may have to wait a minute or two for Ardour to write the file to disk", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
	print (md:run())

	md = nil
	collectgarbage ()

	local md = LuaDialog.Message ("Open Musical Score", "To continue using Ardour you will need to close the Firefox window or the tab the score is open in", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
	print (md:run())

	md = nil
	collectgarbage ()



local sel = Editor:get_selection()
local count = 0
local midi_region

for r in sel.regions:regionlist():iter() do
    count = count + 1
    if r:to_midiregion():isnil() then
       local md = LuaDialog.Message ("Open in Musescore", "The selected region is not a midi", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
	print (md:run())
         md = nil
	collectgarbage ()
        return
    else
        midi_region = r
    end
end

if count ~= 1 then
       local md = LuaDialog.Message ("Open in Musescore", "Please select exactly 1 midi region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
	print (md:run())
         md = nil
	collectgarbage ()
    return
end

local rn = midi_region:name()
local source = midi_region:source(0):to_filesource():path()
print(source)
local filepath = source


local quotedfilepath = '"' .. filepath .. '"'

local command = "mscore -o /tmp/output.pdf  " ..quotedfilepath

os.execute(command)

os.execute("firefox file:///tmp/output.pdf")





end end






