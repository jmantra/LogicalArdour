ardour {
	["type"] = "EditorAction",
	name = "Stem Separation",
	author      = "Justin Ehrlichman",
description = [[
Perform stem separation on an imported song
]]
}

function factory () return function (signal, ...)

local sel = Editor:get_selection()
local count = 0
local midi_region

for r in sel.regions:regionlist():iter() do
    count = count + 1
    if r:to_audioregion():isnil() then
        local md = LuaDialog.Message("Stem Separation", "The selected region is not an audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
        print(md:run())
        md = nil
        collectgarbage()

        return
    else
        audio_region = r
    end
end

if count ~= 1 then
    local md = LuaDialog.Message("Stem Separation", "Please select exactly 1 audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
    print(md:run())
    md = nil
    collectgarbage()
    return
end

local dialog_options = {
  { type = "checkbox", key = "Drums", default = true, title = "Drums" },
  { type = "checkbox", key = "Vocals", default = true, title = "Vocals" },
  { type = "checkbox", key = "Bass", default = true, title = "Bass" },
  { type = "checkbox", key = "Other", default = true, title = "Other" },
}

-- Display the dialog
local od = LuaDialog.Dialog("Select Options", dialog_options)
local rv = od:run()




-- Cleanup the dialog
collectgarbage ()


local rn = audio_region:name()
local source = audio_region:source(0):to_filesource():path()
print(source)
local filepath = source


local quotedfilepath = '"' .. filepath .. '"'


-- Example usage:
local filename = quotedfilepath

rename = "cp "..quotedfilepath.." /home/justin/demucs/input/sep.wav"




 command = 'xterm -e "/home/justin/demucs/run.sh sep.wav"'







-- Open the file "mscore.sh" for writing
local file = io.open("rename.sh", "w")



if not file then
    -- Handle error if file couldn't be opened
    print("Error: Failed to create file 'mscore.sh'")
else
    -- Write the command content to the file


    file:write(rename .. "\n") -- Write the command to the file

    -- Close the file
    file:close()

    print("File 'mscore.sh' created successfully!")

    -- Delete the file after printing the success message

end

local mv = "mv rename.sh /tmp/rename.sh"

os.execute(mv)

chmod = "chmod +x rename.sh"

os.execute(chmod)

os.forkexec("/bin/bash", "/tmp/rename.sh")

os.execute(command)




-- Check if the dialog was confirmed
if rv then
  -- For each option, execute code if the checkbox is selected
  if rv.Drums then
    -- Code to execute if Drums is selected
     local files = C.StringVector()
    print("Drums selected")
       files:push_back("/home/justin/demucs/output/htdemucs/sep/drums.wav")

    local pos = Temporal.timepos_t(0)

    -- Replace ARDOUR.MidiTrackNameSource.SMFFileAndTrackName and other constants with known integer values if they return nil
    Editor:do_import(files,
        Editing.ImportDistinctFiles,  -- Mode
        Editing.ImportAsTrack,        -- Import as Track
        ARDOUR.SrcQuality.SrcBest,    -- Best source quality
        0,                            -- Replace with actual integer if needed
        0,                            -- Replace with actual integer if needed
        pos,
        ARDOUR.PluginInfo(),
        ARDOUR.Track(),
        false
    )


  end

  if rv.Vocals then
    -- Code to execute if Vocals is selected
    print("Vocals selected")
     local files = C.StringVector()



    files:push_back("/home/justin/demucs/output/htdemucs/sep/vocals.wav")

    local pos = Temporal.timepos_t(0)

    -- Replace ARDOUR.MidiTrackNameSource.SMFFileAndTrackName and other constants with known integer values if they return nil
    Editor:do_import(files,
        Editing.ImportDistinctFiles,  -- Mode
        Editing.ImportAsTrack,        -- Import as Track
        ARDOUR.SrcQuality.SrcBest,    -- Best source quality
        0,                            -- Replace with actual integer if needed
        0,                            -- Replace with actual integer if needed
        pos,
        ARDOUR.PluginInfo(),
        ARDOUR.Track(),
        false
    )


  end

  if rv.Bass then
   local files = C.StringVector()
    -- Code to execute if Bass is selected
    print("Bass selected")
     files:push_back("/home/justin/demucs/output/htdemucs/sep/bass.wav")

    local pos = Temporal.timepos_t(0)

    -- Replace ARDOUR.MidiTrackNameSource.SMFFileAndTrackName and other constants with known integer values if they return nil
    Editor:do_import(files,
        Editing.ImportDistinctFiles,  -- Mode
        Editing.ImportAsTrack,        -- Import as Track
        ARDOUR.SrcQuality.SrcBest,    -- Best source quality
        0,                            -- Replace with actual integer if needed
        0,                            -- Replace with actual integer if needed
        pos,
        ARDOUR.PluginInfo(),
        ARDOUR.Track(),
        false
    )

  end

  if rv.Other then
    -- Code to execute if Other is selected
     local files = C.StringVector()
     files:push_back("/home/justin/demucs/output/htdemucs/sep/other.wav")

    local pos = Temporal.timepos_t(0)

    -- Replace ARDOUR.MidiTrackNameSource.SMFFileAndTrackName and other constants with known integer values if they return nil
    Editor:do_import(files,
        Editing.ImportDistinctFiles,  -- Mode
        Editing.ImportAsTrack,        -- Import as Track
        ARDOUR.SrcQuality.SrcBest,    -- Best source quality
        0,                            -- Replace with actual integer if needed
        0,                            -- Replace with actual integer if needed
        pos,
        ARDOUR.PluginInfo(),
        ARDOUR.Track(),
        false
    )
end
end
collectgarbage()







end end





