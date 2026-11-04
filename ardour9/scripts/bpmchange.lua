ardour {
 ["type"] = "EditorAction",
 name = "BPM change - Adjust (timestretch) tempo of an audio",
 author      = "Justin Ehrlichman",
 description = [[
Change the tempo of audio loop in Beats Per Minute (BPM) by uisng either project tempo or entering a tempo manually
]]
}

function factory () 
    return function (signal, ...)
        local sel = Editor:get_selection()
        local count = 0

        for r in sel.regions:regionlist():iter() do
            count = count + 1
            if r:to_audioregion():isnil() then
                local md = LuaDialog.Message("Adjust Tempo", "The selected region is not an audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
                print(md:run())
                md = nil
                collectgarbage()
                return
            else
                audio_region = r
            end
        end

        if count ~= 1 then
            local md = LuaDialog.Message("Adjust Tempo", "Please select exactly 1 audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
            print(md:run())
            md = nil
            collectgarbage()
            return
        end

        local dialog_options = {
            {
                type = "dropdown", 
                key = "dropdown", 
                title = "Choose how you want to adjust BPM", 
                values = {
                    ["Choose how to adjust BPM"] = 1, 
                    ["From project tempo (beginning of timeline)"] = 2,
                    ["Set your BPM"] = 3
                },
                default = "Choose how to adjust BPM"
            }
        }

        -- Create and display the dialog
        ob = LuaDialog.Dialog ("BPM Change", dialog_options)
        av = ob:run()  -- Capture the user input

        -- Check if the user pressed cancel
        if not av then
            return  -- Exit if the user cancels the dialog
        end

        if av and av["dropdown"] == 2 then
            tp = Temporal.timepos_t (Session:nominal_sample_rate () * 1)
            tm = Temporal.TempoMap.read ()
            target_tempo = (tm:quarters_per_minute_at (tp))
            print (tm:quarters_per_minute_at (tp))
            print (target_tempo)
        end

        if av and av["dropdown"] == 3 then
            -- Function to check if the input is a valid 2 or 3 digit number, allowing decimals
            local function is_valid_number(input)
                -- Convert string to number
                local num = tonumber(input)

                -- If the conversion failed, return false
                if not num then
                    return false
                end

                -- Extract the part of the number before the decimal
                local integer_part = input:match("^(%d+)")

                -- Ensure the integer part has 2 or 3 digits
                if integer_part and #integer_part >= 2 and #integer_part <= 3 then
                    return true
                else
                    return false
                end
            end

            -- Function to create and show the main dialog for user input
            local function show_main_dialog()
                local dialog_options = {
                    { type = "entry", key = "text", default = "120", title = "bpm" },
                }
                local od = LuaDialog.Dialog ("Change tempo", dialog_options)
                local rv = od:run()
                return rv  -- Return the dialog result (table or nil)
            end

            -- Function to show error dialog
            local function show_error_dialog()
                local error_dialog_options = {
                    { type = "label", title = "Invalid input! Please enter a 2 or 3 digit number (decimals allowed).", text = "Invalid input! Please enter a 2 or 3 digit number (decimals allowed)." },
                }
                local error_dialog = LuaDialog.Dialog("Invalid Input", error_dialog_options)
                error_dialog:run()  -- Display the error dialog
                error_dialog = nil  -- Clear the error dialog after it closes
            end

            -- Keep asking for input until valid or cancel is pressed
            while true do
                local rv = show_main_dialog()

                -- Exit the script if "Cancel" is pressed (rv is nil)
                if rv == nil then
                    print("Dialog was canceled. Exiting.")
                    return  -- Exit the function
                end

                number = rv["text"]
                print (number)

                if is_valid_number(number) then
                    -- Convert string to a number for mathematical operations
                    numeric_value = tonumber(number)
                    target_tempo = numeric_value
                    break  -- Exit the loop when valid input is received
                else
                    show_error_dialog()  -- Show error dialog if input is invalid
                end
            end
        end

        print(target_tempo)

        local rn = audio_region:name()  -- Get the region name
        print(rn)

        source = audio_region:source(0):to_filesource():path()
        filepath = source

        local quotedfilepath = '"' .. filepath .. '"'

        function extractBPM(rn)
            local bpm = string.match(rn, "(%d%d?%d?)[-_]?%s*[bB][pP][mM]", 1)
            if not bpm then
                bpm = string.match(rn, "[bB][pP][mM]%s*[_-]?(%d+)", 1)
            end
            return bpm
        end

        -- Example usage:
        local bpm = extractBPM(rn)
        if bpm then
            print(bpm)
            local result = bpm

            local md = LuaDialog.Message("Estimate Tempo", result, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
            print(md:run())
            md = nil
            collectgarbage()

            local num = tonumber(result)

            -- to do, add tempo markers and prompt whether or not you want to tempo markers

            -- set a tempo map
            local tm = Temporal.TempoMap.write_copy()
            if dur == true then
                tm:set_tempo(Temporal.Tempo(num, num, 4), st)
                tm:set_tempo(Temporal.Tempo(120, 120, 4), et)
            else
                tp = Temporal.timepos_t (Session:nominal_sample_rate () * 0)
                tm:set_tempo(Temporal.Tempo(num, num, 4), tp)
            end

            Session:begin_reversible_command("Change Tempo Map")
            Temporal.TempoMap.update(tm)
            if not Session:abort_empty_reversible_command() then
                Session:commit_reversible_command(nil)
            end

            tm = nil

            -- Abort Edit example
            -- after every call to Temporal.TempoMap.write_copy()
            -- there must be a matching call to
            -- Temporal.TempoMap.update() or Temporal.TempoMap.abort_update()
            Temporal.TempoMap.write_copy()
            Temporal.TempoMap.abort_update()
        else
            print("BPM not found in filename.")

            local command = "/opt/LogicalArdour/minibpm  " ..quotedfilepath.." > /tmp/bpm.txt"
            os.execute(command)

            -- Read the file
            file = io.open("/tmp/bpm.txt", "r")
            content = file:read("*all")
            file:close()

            -- Extract the number after "Estimated BPM:"
            bpm_string = content:match("Estimated BPM:%s*([%d%.]+)")
            if bpm_string == nil then
                -- Fallback: use sox | bpm if minibpm did not produce a result
                local fallback_command = "sox " .. quotedfilepath .. " -t raw -r 48000 -e float -c 1 - | bpm > /tmp/bpm.txt"
                os.execute(fallback_command)
                file = io.open("/tmp/bpm.txt", "r")
                content = file:read("*all")
                file:close()
                -- Try to extract BPM from the fallback output (assuming bpm outputs just the number or similar)
                bpm_string = content:match("([%d%.]+)")
            end
            bpm_number = tonumber(bpm_string)
            print(bpm_number)
            num = bpm_number

            firstresult = bpm_number
            print(firstresult)

            -- Convert the content to a number and store it in a variable
            current_tempo = tonumber(firstresult)
        end

        -- helper function --
        -- there is currently no direct way to find the track
        -- corresponding to a [selected] region
        function find_track_for_region (region_id)
            for route in Session:get_tracks ():iter () do
                local track = route:to_track ()
                local pl = track:playlist ()
                if not pl:region_by_id (region_id):isnil () then
                    return track
                end
            end
            assert (0) -- can't happen, region must be in a playlist
        end

        print ("blank is "..current_tempo)

        bpmshift = current_tempo/target_tempo

        print(bpmshift)

        -- get Editor selection
        -- http://manual.ardour.org/lua-scripting/class_reference/#ArdourUI:Editor
        -- http://manual.ardour.org/lua-scripting/class_reference/#ArdourUI:Selection
        local sel = Editor:get_selection ()

        -- Instantiate the QM BarBeat Tracker
        -- see http://manual.ardour.org/lua-scripting/class_reference/#ARDOUR:LuaAPI:Vamp
        -- http://vamp-plugins.org/plugin-doc/qm-vamp-plugins.html#qm-barbeattracker
        local vamp = ARDOUR.LuaAPI.Vamp ("libardourvampplugins:qm-barbeattracker", Session:nominal_sample_rate ())

        -- prepare undo operation
        Session:begin_reversible_command ("Rubberband Regions")

        -- for each selected region
        -- http://manual.ardour.org/lua-scripting/class_reference/#ArdourUI:RegionSelection
        for r in sel.regions:regionlist ():iter () do
            -- "r" is-a http://manual.ardour.org/lua-scripting/class_reference/#ARDOUR:Region

            -- test if it's an audio region
            local ar = r:to_audioregion ()
            if ar:isnil () then
                goto next
            end

            -- create Rubberband stretcher
            local rb = ARDOUR.LuaAPI.Rubberband (ar, false)

            -- the rubberband-filter also implements the readable API.
            -- https://manual.ardour.org/lua-scripting/class_reference/#ARDOUR:AudioReadable
            -- This allows to read from the master-source of the given audio-region.
            -- Any prior time-stretch or pitch-shift are ignored when reading, however
            -- processing retains the previous settings
            local max_pos = rb:readable ():readable_length ()

            -- prepare table to hold analysis results
            -- the beat-map is a table holding audio-sample positions:
            -- [from] = to
            local beat_map = {}
            local prev_beat = 0

            -- construct a progress-dialog with cancel button
            local pdialog = LuaDialog.ProgressWindow ("Rubberband", true)
            -- progress dialog callbacks
            function vamp_callback (_, pos)
                return pdialog:progress (pos / max_pos, "Analyzing")
            end
            function rb_progress (_, pos)
                return pdialog:progress (pos / max_pos, "Stretching")
            end

            -- run VAMP plugin, analyze the first channel of the audio-region
            vamp:analyze (rb:readable (), 0, vamp_callback)

            -- getRemainingFeatures returns a http://manual.ardour.org/lua-scripting/class_reference/#Vamp:Plugin:FeatureSet
            -- get the first output. here: Beats, estimated beat locations & beat-number
            -- "fl" is-a http://manual.ardour.org/lua-scripting/class_reference/#Vamp:Plugin:FeatureList
            local fl = vamp:plugin ():getRemainingFeatures ():at (0)
            local beatcount = 0
            -- iterate over returned features
            for f in fl:iter () do
                -- "f" is-a  http://manual.ardour.org/lua-scripting/class_reference/#Vamp:Plugin:Feature
                local fn = Vamp.RealTime.realTime2Frame (f.timestamp, Session:nominal_sample_rate ())
                beat_map[fn] = fn -- keep beats (1/4 notes) unchanged
                if prev_beat > 0 then
                    -- move the half beats (1/8th) back
                    local diff = (fn - prev_beat) / 2
                    beat_map[fn - diff] = fn - diff + diff / 3 -- moderate swing 2:1 (triplet)
                    --beat_map[fn - diff] = fn - diff + diff / 2 -- hard swing 3:1 (dotted 8th)
                    beatcount = beatcount + 1
                end
                prev_beat = fn
            end
            -- reset the plugin state (prepare for next iteration)
            vamp:reset ()

            if pdialog:canceled () then goto out end

            -- skip regions shorter than a bar
            if beatcount < 8 then
                pdialog:done ()
                goto next
            end

            -- configure rubberband stretch tool
            rb:set_strech_and_pitch (bpmshift, 1) -- no overall stretching, no pitch-shift
            --rb:set_mapping (beat_map) -- apply beat-map from/to

            -- now stretch the region
            local nar = rb:process (rb_progress)

            if pdialog:canceled () then goto out end

            -- hide modal progress dialog and destroy it
            pdialog:done ()
            pdialog = nil

            -- replace region
            if not nar:isnil () then
                print ("new audio region: ", nar:name (), nar:length ())
                local track = find_track_for_region (r:to_stateful ():id ())
                local playlist = track:playlist ()
                playlist:to_stateful ():clear_changes () -- prepare undo
                playlist:remove_region (r)
                playlist:add_region (nar, r:position (), 1, false)
                -- create a diff of the performed work, add it to the session's undo stack
                -- and check if it is not empty
                Session:add_stateful_diff_command (playlist:to_statefuldestructible ())
            end

            ::next::
        end

        ::out::

        -- all done, commit the combined Undo Operation
        if not Session:abort_empty_reversible_command () then
            Session:commit_reversible_command (nil)
        end
    end
end

