ardour {
	["type"] = "EditorAction",
	name = "Open Midi region in Musescore",
	author      = "Justin Ehrlichman",
description = [[
Open up selected midi region in musescore
]]
}

function factory () return function (signal, ...)



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
local filepath = Session:path() .. "/interchange/" .. Session:name() .. "/midifiles/" .. rn .. ".mid"



-- Add the cron job to launch MuseScore
local cronJobCmd = string.format([[crontab -l | grep -q 'DISPLAY=:0.0 /usr/bin/mscore "%s"' || (crontab -l; echo '*/1 * * * * DISPLAY=:0.0 /usr/bin/mscore "%s" &') | crontab -]], filepath, filepath)
os.execute(cronJobCmd)

	local md = LuaDialog.Message ("Open in Musescore", "Please wait up to 1 minute for musescore, if Ardour crashes before musescore please run the following command in your terminal: crontab -r", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
	print (md:run())

	md = nil
	collectgarbage ()


os.execute("sleep 55")
os.execute("crontab -r")
end end 

