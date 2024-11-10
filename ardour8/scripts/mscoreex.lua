ardour {
	["type"] = "EditorAction",
	name = "Musescore - Open Midi region in musical notation format",
	author      = "Justin Ehrlichman",
description = [[
Takes a selected MIDI region and opens it in Musescore
]]
}

function factory () return function (signal, ...)

local md = LuaDialog.Message ("Open Musical Score", "If Musescore shows a blank page, you may have to wait a minute or two for Ardour to write the file to disk", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
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
 route = midi_region:playlist():name()
print ( track)
	pid = midi_region:playlist():get_orig_track_id ()
print (pid)


local quotedfilepath = '"' .. filepath .. '"'

local command = "mscore -a jack -o /tmp/output.pdf  " ..quotedfilepath

-- Open the file "mscore.sh" for writing
local file = io.open("mscore.sh", "w")



if not file then
    -- Handle error if file couldn't be opened
    print("Error: Failed to create file 'mscore.sh'")
else
    -- Write the command content to the file


    file:write(command .. "\n") -- Write the command to the file

    -- Close the file
    file:close()

    print("File 'mscore.sh' created successfully!")

    -- Delete the file after printing the success message

end

local mv = "mv mscore.sh /tmp/mscore.sh"

os.execute(mv)

os.forkexec("/bin/bash", "/tmp/mscore.sh")

--os.execute("firefox file:///tmp/output.pdf")

 os.remove("/tmp/mscore.sh")



-- Open the file "mscore.sh" for writing
local file = io.open("mscore.sh", "w")



if not file then
    -- Handle error if file couldn't be opened
    print("Error: Failed to create file 'mscore.sh'")
else
    -- Write the command content to the file
 local command = "mscore " ..quotedfilepath

    file:write(command .. "\n") -- Write the command to the file

    -- Close the file
    file:close()

    print("File 'mscore.sh' created successfully!")

    -- Delete the file after printing the success message

end

local mv = "mv mscore.sh /tmp/mscore.sh"

os.execute(mv)

os.forkexec("/bin/bash", "/tmp/mscore.sh")

for r in Session:get_routes ():iter () do
   if not r:to_track ():isnil () and not r:to_track ():to_midi_track ():isnil () then




os.execute("sleep 5")




local proc = Session:route_by_id(pid):to_track()

				local inputmidiport = r:input():midi(0)
				-- print(inputmidiport:name())
                                print (proc:name())
                                inputmidiport:disconnect("mscore:mscore-midi-1")
                                 local correctport = proc:input():midi(0)


				 correctport:connect("mscore:mscore-midi-1")
			end
	end








end end





