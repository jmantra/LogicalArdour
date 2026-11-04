ardour {
    ["type"] = "EditorAction",
    name = "Drum Velocity Control",
    author = "Justin Ehrlichman",
    description = [[
    Adjusts the velocity of all notes in a drum loop based on a slider value.
    At 100%, no notes are affected. At 0%, all notes have zero velocity.
    ]]
}

function factory()
    return function()
        -- Get the current editor selection
        local sel = Editor:get_selection()
        local count = 0
        local midi_region

        -- Check if we have exactly one MIDI region selected
        for r in sel.regions:regionlist():iter() do
            count = count + 1
            if r:to_midiregion():isnil() then
                local md = LuaDialog.Message("Drum Velocity", "The selected region is not a MIDI region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
                print(md:run())
                md = nil
                collectgarbage()
                return
            else
                midi_region = r
            end
        end

        if count ~= 1 then
            local md = LuaDialog.Message("Drum Velocity", "Please select exactly 1 MIDI region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
            print(md:run())
            md = nil
            collectgarbage()
            return
        end

        -- Create dialog with slider
        local dialog_options = {
            {
                type = "slider",
                key = "velocity",
                title = "Velocity Control",
                min = 0,
                max = 100,
                default = 100,
                step = 1
            }
        }

        local od = LuaDialog.Dialog("Drum Velocity Control", dialog_options)
        local rv = od:run()

        if not rv then
            return -- User cancelled
        end

        -- Get the velocity percentage from the slider
        local velocity_percent = rv["velocity"]
        
        -- Begin undoable operation
        Session:begin_reversible_command("Adjust Drum Velocities")

        -- Get the MIDI source and model
        local midi_source = midi_region:to_midiregion():midi_source(0)
        local model = midi_source:model()
        
        -- Create a new note diff command
        local midi_command = model:new_note_diff_command("Adjust Velocities")

        -- Get all notes and iterate through them
        local notes = midi_source:get_notes()
        for note in notes:iter() do
            -- Calculate new velocity based on percentage
            local new_velocity = math.floor((note:velocity() * velocity_percent) / 100)
            
            -- Create a new note with the adjusted velocity
            local new_note = ARDOUR.LuaAPI.new_noteptr(
                note:channel(),
                note:time(),
                note:length(),
                note:note(),
                new_velocity
            )
            
            -- Add the modified note to the command
            midi_command:add(new_note)
        end

        -- Apply the changes
        model:apply_command(Session, midi_command)
        
        -- End the undoable operation
        Session:commit_reversible_command()
    end
end 