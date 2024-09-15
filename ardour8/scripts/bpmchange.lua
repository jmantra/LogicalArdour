ardour {
 ["type"] = "EditorAction",
 name = "BPM change - Adjust (timestretch) tempo of an audio",
 author      = "Justin Ehrlichman",
 description = [[
Change the tempo of audio loop in Beats Per Minute (BPM) by uisng either project tempo or entering a tempo manually
]]
}

function factory () return function (signal, ...)

local sel = Editor:get_selection()
local count = 0
local midi_region

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
   type = "dropdown", key = "dropdown", title = "Choose how you want to adjust BPM", values =
   {
    ["Choose how to adjust BPM"] = 1, ["From project tempo (beginning of timeline)"] = 2,
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

	target_tempo =  (tm:quarters_per_minute_at (tp))

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


-- Function to remove the BPM pattern from the region name
-- Function to extract BPM pattern from the region name
function extractBPM(rn)
    local bpm = string.match(rn, "(%d%d?%d?)[-_]?%s*[bB][pP][mM]", 1)
    if not bpm then
        bpm = string.match(rn, "[bB][pP][mM]%s*[_-]?(%d+)", 1)
    end
    return bpm
end

-- Function to remove the BPM pattern from the region name
function removeBPM(rn)
    -- Remove the patterns matching BPM (e.g., "120-bpm" or "bpm-120")
    local cleaned_name = rn:gsub("(%d%d?%d?)[-_]?%s*[bB][pP][mM]", "")
    cleaned_name = cleaned_name:gsub("[bB][pP][mM]%s*[_-]?(%d+)", "")
    -- Trim any leading/trailing spaces
    cleaned_name = cleaned_name:match("^%s*(.-)%s*$")
    return cleaned_name
end

-- Example usage:
local bpm = extractBPM(rn)
if bpm then
    print("BPM found:", bpm)

    current_tempo = bpm

    -- Remove BPM from the region name
    local new_name = removeBPM(rn)
    print("Renaming region to:", new_name)

    -- Rename the audio region
    audio_region:set_name(new_name)


else
    print("No BPM found in region name.")

  -- ratio - current_tempo/target_tempo

     -- get Editor selection
    local sel = Editor:get_selection ()

    -- Instantiate the QM BarBeat Tracker
    local vamp = ARDOUR.LuaAPI.Vamp("libardourvampplugins:qm-barbeattracker", Session:nominal_sample_rate())

    -- prepare tables to hold results
    local beats = {}
    local bars = {}

    -- for each selected region
    for r in sel.regions:regionlist ():iter () do
        local ar = r:to_audioregion ()
        if ar:isnil () then
            goto next
        end

        beats[r:name ()] = {}
        bars[r:name ()] = {}

        -- callback to handle Vamp-Plugin analysis results
        function callback (feats)
            local fl = feats:table()[0]
            if fl then
                for f in fl:iter () do
                    if f.hasTimestamp then
                        local fn = Vamp.RealTime.realTime2Frame(f.timestamp, 48000)
                        table.insert(beats[r:name ()], {pos = fn, beat = tonumber(f.label)})
                    end
                end
            end

            local fl = feats:table()[1]
            if fl then
                for f in fl:iter () do
                    if f.hasTimestamp then
                        local fn = Vamp.RealTime.realTime2Frame(f.timestamp, 48000)
                        table.insert(bars[r:name ()], fn)
                    end
                end
            end
            return false -- continue, don't cancel
        end

        vamp:plugin():setParameter("Beats Per Bar", 4)

        vamp:analyze(ar:to_readable(), 0, callback)
        callback(vamp:plugin():getRemainingFeatures())
        vamp:reset()
        ::next::
    end

    -- Calculate distances between beats, ignoring the first Beat 4, and then average
    local first_beat_4_skipped = false
    local total_distance = 0
    local distance_count = 0

    for n, o in pairs(beats) do
        print("Distance between beats for region:", n)

        -- Iterate over the beats
        for i = 2, #o do
            local current_beat = o[i]['beat']
            local previous_beat = o[i-1]['beat']

            -- Skip the first occurrence of Beat 4
            if current_beat == 4 and not first_beat_4_skipped then
                first_beat_4_skipped = true
            else
                local distance = o[i]['pos'] - o[i-1]['pos']
                total_distance = total_distance + distance
                distance_count = distance_count + 1
                print("Distance between Beat " .. previous_beat .. " and Beat " .. current_beat .. ":", distance, "samples")
            end
        end
    end

    -- Calculate and print the average distance
    if distance_count > 0 then
        local average_distance = total_distance / distance_count
        print("Average distance between beats (excluding the first Beat 4):", average_distance, "samples")
    current_tempo = 48000/average_distance * 60
  print (current_tempo)

    else
        print("No distances calculated.")

        -- local command = "bpmbin " .. quotedfilepath

        local command = "sox  " ..quotedfilepath.. " -t raw -r 48000  -e float -c 1 - | bpm"

os.execute(command)


-- Open the file in write mode



   local handle = io.popen(command)
    local firstresult = handle:read("*a")
    handle:close()

    print(firstresult)

    -- Convert the content to a number and store it in a variable
     current_tempo = tonumber(firstresult)

    end
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

end end

