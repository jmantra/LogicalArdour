ardour {
	["type"] = "EditorAction",
	name = "Musescore - Open Midi region in Musescore",
	author      = "Justin Ehrlichman",
description = [[
Open up selected midi region in musescore
]]
}

function factory () return function (signal, ...)

local md = LuaDialog.Message ("Open in Musescore", "If Musescore shows a blank page, you may have to wait a minute or two for Ardour to write the file to disk", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
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





-- Add the cron job to launch MuseScore
local cronJobCmd = string.format([[crontab -l | grep -q 'DISPLAY=:0.0 /usr/bin/mscore "%s"' || (crontab -l; echo '*/1 * * * * DISPLAY=:0.0 /usr/bin/mscore "%s" &') | crontab -]], filepath, filepath)
os.execute(cronJobCmd)

	local md = LuaDialog.Message ("Open in Musescore", "Please wait up to 1 minute for musescore, if Ardour crashes before musescore please run the following command in your terminal: crontab -r", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
	print (md:run())

	md = nil
	collectgarbage ()

-- Lua script to continuously check for the mscore process and remove crontab if it launches

local function checkProcess(processName)
    local handle = io.popen('pgrep -x ' .. processName)
    local result = handle:read("*a")
    handle:close()
    return #result > 0
end

local function removeCrontab()
    os.execute('crontab -r')
end

-- Main loop
while true do
    -- Check if mscore process is running
    if checkProcess('mscore') then
        print("mscore process detected. Removing crontab...")
        removeCrontab()
        print("Crontab removed.")
        break  -- Exit the loop once crontab is removed, change this if you want to continuously check
    end
    -- Adjust sleep time according to your needs
    os.execute('sleep 5') -- Check every 5 seconds
end

end end












