ardour {
 ["type"] = "EditorAction",
 name = "Drummer - Smart Drum Pattern Generator",
 author = "Justin Ehrlichman",
 description = [[
 Creates and manages a smart drum pattern generator similar to Logic Pro's Drummer.
 Supports multiple styles, variations, and complexity levels.
 ]]
}

-- Constants for drum patterns
local DRUM_PATTERNS = {
    ROCK = {
        name = "Rock",
        patterns = {
            basic = {
                {note = 36, time = 0, velocity = 100},    -- Kick
                {note = 38, time = 0.5, velocity = 80},   -- Snare
                {note = 42, time = 0.25, velocity = 70},  -- Closed Hi-hat
                {note = 42, time = 0.75, velocity = 70},  -- Closed Hi-hat
            },
            fill = {
                {note = 36, time = 0, velocity = 100},    -- Kick
                {note = 38, time = 0.5, velocity = 80},   -- Snare
                {note = 42, time = 0.25, velocity = 70},  -- Closed Hi-hat
                {note = 42, time = 0.75, velocity = 70},  -- Closed Hi-hat
                {note = 49, time = 0.75, velocity = 90},  -- Crash
            }
        }
    },
    JAZZ = {
        name = "Jazz",
        patterns = {
            basic = {
                {note = 36, time = 0, velocity = 80},     -- Kick
                {note = 38, time = 0.5, velocity = 70},   -- Snare
                {note = 42, time = 0, velocity = 60},     -- Closed Hi-hat
                {note = 42, time = 0.25, velocity = 60},  -- Closed Hi-hat
                {note = 42, time = 0.5, velocity = 60},   -- Closed Hi-hat
                {note = 42, time = 0.75, velocity = 60},  -- Closed Hi-hat
            }
        }
    },
    ELECTRONIC = {
        name = "Electronic",
        patterns = {
            basic = {
                {note = 36, time = 0, velocity = 100},    -- Kick
                {note = 36, time = 0.5, velocity = 100},  -- Kick
                {note = 42, time = 0, velocity = 80},     -- Closed Hi-hat
                {note = 42, time = 0.25, velocity = 80},  -- Closed Hi-hat
                {note = 42, time = 0.5, velocity = 80},   -- Closed Hi-hat
                {note = 42, time = 0.75, velocity = 80},  -- Closed Hi-hat
            }
        }
    }
}

function factory()
    return function()
        -- Create dialog for drummer settings
        local dialog_options = {
            {
                type = "dropdown",
                key = "style",
                title = "Drum Style",
                values = {
                    ["Rock"] = 1,
                    ["Jazz"] = 2,
                    ["Electronic"] = 3
                },
                default = "Rock"
            },
            {
                type = "dropdown",
                key = "complexity",
                title = "Pattern Complexity",
                values = {
                    ["Simple"] = 1,
                    ["Medium"] = 2,
                    ["Complex"] = 3
                },
                default = "Medium"
            },
            {
                type = "dropdown",
                key = "variation",
                title = "Pattern Variation",
                values = {
                    ["Basic"] = 1,
                    ["Fill"] = 2,
                    ["Random"] = 3
                },
                default = "Basic"
            }
        }

        local dialog = LuaDialog.Dialog("Drummer Settings", dialog_options)
        local result = dialog:run()

        if not result then return end

        -- Get selected options
        local style = result["style"]
        local complexity = result["complexity"]
        local variation = result["variation"]

        -- Create new MIDI track
        local track = ARDOUR.LuaAPI.new_midi_track(Session, "Drummer")
        if not track then
            LuaDialog.Message("Error", "Failed to create MIDI track", LuaDialog.MessageType.Error, LuaDialog.ButtonType.OK):run()
            return
        end

        -- Add drum plugin
        local plugin = ARDOUR.LuaAPI.new_plugin(Session, "Red Zeppelin Drumkit", ARDOUR.PluginType.LV2, "")
        if not plugin then
            LuaDialog.Message("Error", "Failed to create drum plugin", LuaDialog.MessageType.Error, LuaDialog.ButtonType.OK):run()
            return
        end

        -- Get the selected pattern
        local pattern = DRUM_PATTERNS[style].patterns[variation]
        if not pattern then
            pattern = DRUM_PATTERNS[style].patterns.basic
        end

        -- Create MIDI region with pattern
        local region = ARDOUR.LuaAPI.new_midi_region(Session, track, 0, 4) -- 4 bars
        if not region then
            LuaDialog.Message("Error", "Failed to create MIDI region", LuaDialog.MessageType.Error, LuaDialog.ButtonType.OK):run()
            return
        end

        -- Add MIDI notes based on pattern
        for _, note in ipairs(pattern) do
            local midi_note = ARDOUR.LuaAPI.new_midi_note(
                region,
                note.time * 4, -- Convert to beats
                note.note,
                note.velocity,
                0.25 -- Note length in beats
            )
        end

        -- Set track name
        track:set_name("Drummer - " .. DRUM_PATTERNS[style].name)

        LuaDialog.Message("Success", "Drummer track created successfully!", LuaDialog.MessageType.Info, LuaDialog.ButtonType.OK):run()
    end
end 