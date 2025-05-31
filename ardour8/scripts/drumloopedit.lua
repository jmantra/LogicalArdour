ardour {
    ["type"] = "EditorAction",
    name = "Drum Loop Editor",
    license = "MIT",
    author = "Justin Ehrlichman",
    description = "Dynamically adds and 'removes' drum notes from a midi drum loop based on a percentage.'Removes' is in quotes because it doesn't actually remove the note just turns off (or back on) the velocity of  existing notes."
}

function factory () return function ()
    local sel = Editor:get_selection()
    local midi_region = nil

    -- Find the selected MIDI region
    for r in sel.regions:regionlist():iter() do
        midi_region = r:to_midiregion()
        if midi_region then break end
    end

    if not midi_region then
        LuaDialog.Message("Add Notes to MIDI", "No MIDI region selected.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
        return
    end

    -- Set this to true for debugging output in the scripting console.
    local debug = false

    -- Set this to true to prompt for the velocity parameters.
    local interactive = true

    -- Set this to the default velocities and instrument states
    local param = {
        kick_vel = 100,
        snare_vel = 100,
        closed_hat_vel = 100,
        open_hat_vel = 100,
        tom_vel = 100,
        clap_vel = 100,
        tamb_vel = 100,
        maraca_vel = 100,
        kick_percent = 0,
        snare_percent = 0,
        closed_hat_percent = 0,
        open_hat_percent = 0,
        tom_percent = 0,
        clap_percent = 0,
        tamb_percent = 0,
        maraca_percent = 0,
        kick_enabled = false,
        snare_enabled = false,
        closed_hat_enabled = false,
        open_hat_enabled = false,
        tom_enabled = false,
        clap_enabled = false,
        tamb_enabled = false,
        maraca_enabled = false
    }

    -- Don't load any saved state - always use defaults
    -- if meter_global_param then
    --    param.kick_vel = meter_global_param.kick_vel
    --    param.snare_vel = meter_global_param.snare_vel
    --    param.clap_vel = meter_global_param.clap_vel
    --    param.tamb_vel = meter_global_param.tamb_vel
    --    param.maraca_vel = meter_global_param.maraca_vel
    -- end

    -- Define instruments with their MIDI notes
    local instruments = {
        {name = "Kick", pitch = 36, min_notes = 1, max_notes = 3},
        {name = "Snare", pitch = 38, min_notes = 1, max_notes = 3},
        {name = "Closed Hat", pitch = 42, min_notes = 1, max_notes = 3},
        {name = "Open Hat", pitch = 46, min_notes = 1, max_notes = 3},
        {name = "Tom", pitch = 41, min_notes = 1, max_notes = 3},
        {name = "Clap", pitch = 39, min_notes = 1, max_notes = 3},
        {name = "Tamb", pitch = 54, min_notes = 1, max_notes = 3},
        {name = "Maraca", pitch = 70, min_notes = 1, max_notes = 3}
    }

    if interactive then
       local dialog_options = {
          { type = "label", title = "Drum Loop Editor" },
       }

       -- Add controls for all instruments
       for _, instrument in ipairs(instruments) do
          local vel_key = instrument.name:lower():gsub(" ", "_") .. "_vel"
          local percent_key = instrument.name:lower():gsub(" ", "_") .. "_percent"
          local enabled_key = instrument.name:lower():gsub(" ", "_") .. "_enabled"
          
          -- Add checkbox for instrument selection
          table.insert(dialog_options, {
             type = "checkbox",
             key = enabled_key,
             title = "Change " .. instrument.name,
             default = false
          })
          
          -- Add percentage input box for note placement
          table.insert(dialog_options, {
             type = "slider",
             key = percent_key,
             title = "Add "..instrument.name .." by percentage" ,
             min = 0,
             max = 100,
             step = 1,
             digits = 0,
             default = 0
          })
          
          -- Add velocity slider
          table.insert(dialog_options, {
             type = "slider",
             key = vel_key,
             title = instrument.name .. " On/Off Probability",
             min = 0,
             max = 100,
             step = 1,
             digits = 0,
             default = 100
          })
          
          table.insert(dialog_options, {
             type = "button",
             key = "reset_" .. instrument.name:lower(),
             title = "Reset " .. instrument.name .. " Settings"
          })

          -- Add separator between instruments
          if instrument.name ~= "Maraca" then
             table.insert(dialog_options, { type = "separator" })
          end
       end

       local dg = LuaDialog.Dialog("Drum Pattern Setup", dialog_options)
       local result = dg:run()
       if result then
          -- Update all parameters
          for _, instrument in ipairs(instruments) do
             local vel_key = instrument.name:lower():gsub(" ", "_") .. "_vel"
             local percent_key = instrument.name:lower():gsub(" ", "_") .. "_percent"
             local enabled_key = instrument.name:lower():gsub(" ", "_") .. "_enabled"
             local reset_key = "reset_" .. instrument.name:lower()

             -- Handle reset buttons
             if result[reset_key] then
                param[vel_key] = 100
                param[percent_key] = 0
                param[enabled_key] = false
             end

             param[vel_key] = result[vel_key]
             param[percent_key] = result[percent_key]
             param[enabled_key] = result[enabled_key]
             instrument.enabled = param[enabled_key] and result[percent_key] > 0
             instrument.placement_percent = result[percent_key]
          end

          -- save the data for the next invocation
          meter_global_param = param
       else
          -- dialog canceled, exit
          return
       end
    end

    local sel = Editor:get_selection ()
    for r in sel.regions:regionlist ():iter () do
       local mr = r:to_midiregion ()
       if not mr:isnil() then
          local mm = mr:model ()
          local nl = ARDOUR.LuaAPI.note_list (mm)
          local mc = mm:new_note_diff_command ("Drum Velocity")
          
          for n in nl:iter () do
             local vel = n:velocity ()
             local note = n:note()

             -- Check if it's a kick or snare note and apply velocity reduction
             if note == 36 and param.kick_enabled then -- Kick
                if param.kick_vel < 100 then
                   -- For values less than 100, randomly set velocity to 0 or max
                   if math.random(100) > param.kick_vel then
                      vel = 0
                   else
                      vel = 127
                   end
                else
                   -- When kick_vel is 100, restore maximum velocity
                   vel = 127
                end
             end
             if note == 38 and param.snare_enabled then -- Snare
                if param.snare_vel < 100 then
                   -- For values less than 100, randomly set velocity to 0 or max
                   if math.random(100) > param.snare_vel then
                      vel = 0
                   else
                      vel = 127
                   end
                else
                   -- When snare_vel is 100, restore maximum velocity
                   vel = 127
                end
             end
             if note == 42 and param.closed_hat_enabled then -- Closed Hi-hat
                if param.closed_hat_vel < 100 then
                   -- For values less than 100, randomly set velocity to 0 or max
                   if math.random(100) > param.closed_hat_vel then
                      vel = 0
                   else
                      vel = 127
                   end
                else
                   -- When closed_hat_vel is 100, restore maximum velocity
                   vel = 127
                end
             end
             if note == 46 and param.open_hat_enabled then -- Open Hi-hat
                if param.open_hat_vel < 100 then
                   if math.random(100) > param.open_hat_vel then
                      vel = 0
                   else
                      vel = 127
                   end
                else
                   vel = 127
                end
             end
             if note == 41 and param.tom_enabled then -- Tom
                if param.tom_vel < 100 then
                   if math.random(100) > param.tom_vel then
                      vel = 0
                   else
                      vel = 127
                   end
                else
                   vel = 127
                end
             end
             if note == 39 and param.clap_enabled then -- Clap
                if param.clap_vel < 100 then
                   if math.random(100) > param.clap_vel then
                      vel = 0
                   else
                      vel = 127
                   end
                else
                   vel = 127
                end
             end
             if note == 54 and param.tamb_enabled then -- Tamb
                if param.tamb_vel < 100 then
                   if math.random(100) > param.tamb_vel then
                      vel = 0
                   else
                      vel = 127
                   end
                else
                   vel = 127
                end
             end
             if note == 70 and param.maraca_enabled then -- Maraca
                if param.maraca_vel < 100 then
                   if math.random(100) > param.maraca_vel then
                      vel = 0
                   else
                      vel = 127
                   end
                else
                   vel = 127
                end
             end

             -- Only modify the note if velocity changed
             if vel ~= n:velocity() then
                local n2 = ARDOUR.LuaAPI.new_noteptr(n:channel(), n:time(), n:length(), n:note(), vel)
                mc:remove(n)
                mc:add(n2)
             end
          end
          mm:apply_command(Session, mc)
       end
    end

    local mm = midi_region:midi_source(0):model()
    local midi_command = mm:new_note_diff_command("AddRandomNotes")

    local tm = Temporal.TempoMap.read()
    local midi_start = midi_region:position()
    local midi_end = midi_start + midi_region:length()

    -- Calculate beat positions
    local meter = tm:meter_at(midi_start)
    local beats_per_bar = meter:divisions_per_bar()
    local sr = Session:nominal_sample_rate()

    -- Get tempo at start to estimate beat length
    local tempo = tm:tempo_at(midi_start)
    local bpm = tempo:note_types_per_minute()
    local seconds_per_beat = 60.0 / bpm
    local samples_per_beat = seconds_per_beat * sr

    -- Find all beat positions within the region
    local beat_positions = {}
    local region_length_samples = midi_region:length():samples()

    -- Start from the beginning of the region and add beat intervals
    local current_offset = 0
    while current_offset < region_length_samples do
        local beat_position = midi_start + Temporal.timecnt_t(math.floor(current_offset))
        table.insert(beat_positions, beat_position)
        current_offset = current_offset + samples_per_beat
    end

    -- Generate random notes for each enabled instrument at beat positions
    for _, instrument in ipairs(instruments) do
        local enabled_key = instrument.name:lower():gsub(" ", "_") .. "_enabled"
        if param[enabled_key] and instrument.enabled then
            local vel_key = instrument.name:lower():gsub(" ", "_") .. "_vel"
            local velocity_percentage = param[vel_key]
            local placement_percentage = instrument.placement_percent

            -- Select beats based on placement percentage
            local selected_beats = {}
            for i = 1, #beat_positions do
                if math.random(100) <= placement_percentage then
                    table.insert(selected_beats, i)
                end
            end

            -- Determine which of those notes will be active based on velocity percentage
            local active_beats = {}
            for i = 1, #selected_beats do
                if math.random(100) <= velocity_percentage then
                    table.insert(active_beats, selected_beats[i])
                end
            end

            -- Create notes at selected beat positions
            for _, beat_index in ipairs(selected_beats) do
                local beat_position = beat_positions[beat_index]

                -- Random length between 0.1 and 0.5 seconds
                local random_length = 0.1 + math.random() * 0.4

                -- Set velocity based on whether this note is in the active set
                local random_velocity = 0
                for _, active_beat in ipairs(active_beats) do
                    if active_beat == beat_index then
                        random_velocity = 127
                        break
                    end
                end

                local sr = Session:nominal_sample_rate()
                local len_samples = Temporal.timecnt_t(math.floor(random_length * sr))
                local pos = tm:quarters_at(beat_position, 0)
                local len = tm:quarters_at(beat_position + len_samples, 0) - pos

                local new_note = ARDOUR.LuaAPI.new_noteptr(0, pos, len, instrument.pitch, random_velocity)
                midi_command:add(new_note)
            end
        end
    end

    mm:apply_command(Session, midi_command)
end end
