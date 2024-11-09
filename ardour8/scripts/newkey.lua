ardour {
    ["type"] = "EditorAction",
    name = "Pitch - Adjust pitch of audio loop by key",
    author = "Justin Ehrlichman",
    description = [[
Transposes the key of audio loop
]]
}

function factory()
    return function(signal, ...)

    -- Get the user config directory
local user_config_directory = ARDOUR.user_config_directory(8)

-- Construct the full path to the key.txt file
local key_file_path = user_config_directory .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

-- Prepare the dialog option with the file content
local current_key_option = "Set to current project key: " .. file_content
        local sel = Editor:get_selection()
        local count = 0
        local audio_region

        for r in sel.regions:regionlist():iter() do
            count = count + 1
            if r:to_audioregion():isnil() then
                local md = LuaDialog.Message("Get Key", "The selected region is not an audio region. The  project key is currently set to "..file_content, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
                print(md:run())
                md = nil
                collectgarbage()
                return
            else
                audio_region = r
            end
        end

        if count ~= 1 then
            local md = LuaDialog.Message("Get Key", "Please select exactly 1 audio region. The project key is currently set to "..file_content, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
            print(md:run())
            md = nil
            collectgarbage()
            return
        end

        local rn = audio_region:name()
        local source = audio_region:source(0):to_filesource():path()
        print(source)
        local filepath = source
        local quotedfilepath = '"' .. filepath .. '"'

        -- Example usage:
      --  local filename = quotedfilepath

        -- Pattern to capture the key after "key_"
    local fkey = rn:match("key_([A-G][#b]?m?)")

    if fkey then
        print("Extracted key:", fkey)

        if fkey:find("m$") then
            fkey = fkey .. " minor"
        else
            fkey = fkey .. " major"
        end

        dkey = fkey
        print("Extracted key from file:", dkey)
        cname = true
        else


            firstresult = "Key not found."
            local command = "key " .. quotedfilepath
            os.execute(command)

            -- Open the file in write mode
            local handle = io.popen(command)
            firstresult = handle:read("*a")
            handle:close()
            print(firstresult)

-- Extract the key and scale
local dkey, scale = string.match(firstresult, "The key of the song is ([A-G#]+) (%a+)")

-- If the scale is minor, append 'm' to the key
-- Extract the key and scale
local dkey, scale = string.match(firstresult, "The key of the song is ([A-Gb#]+) (%a+)")

-- If the scale is minor, append 'm' to the key
if scale == "minor" then
    dkey = dkey .. "m"
end

print("Key: " .. dkey)
print("Scale: " .. scale)

end



-- Get the user config directory
local user_config_directory = ARDOUR.user_config_directory(8)

-- Construct the full path to the key.txt file
local key_file_path = user_config_directory .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

-- Prepare the dialog option with the file content
local current_key_option = "Set to current project key: " .. file_content

if cname == true then

sentence = "Estimated key of loop: " .. dkey ..  ". Choose Target Key (Hit Cancel or select Do not change key to not change the key)"
else

sentence = "Estimated key of loop: " .. dkey .. " " .. scale .. ". Choose Target Key (Hit Cancel or select Do not change key to not change the key)"

end

local dialog_options = {
  {
   type = "dropdown", key = "target_key", title = sentence, values =
   {
    ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
    ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
    ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
    ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
    ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
    ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
    [current_key_option] = 35, -- Add the file content option
    ["Do not change key"] = 36 -- Update index for "Do not change key" to avoid overlap
   },
   default = current_key_option -- Set the current key option as the default
  }
}

-- Create and run the dialog
local od = LuaDialog.Dialog("Choose Target Key", dialog_options)
local rv = od:run()


-- Create a reverse lookup table to map numbers back to musical key strings
local number_to_key = {
    [1] = "C", [2] = "C#", [3] = "Db", [4] = "D", [5] = "D#", [6] = "Eb",
    [7] = "E", [8] = "F", [9] = "F#", [10] = "Gb", [11] = "G", [12] = "G#", [13] = "Ab",
    [14] = "A", [15] = "A#", [16] = "Bb", [17] = "B",
    [18] = "Am", [19] = "A#m", [20] = "Bbm", [21] = "Bm", [22] = "Cm",
    [23] = "C#m", [24] = "Dbm", [25] = "Dm", [26] = "D#m", [27] = "Ebm",
    [28] = "Em", [29] = "Fm", [30] = "F#m", [31] = "Gbm", [32] = "Gm", [33] = "G#m", [34] = "Abm"
}

-- Check the user's selection
if rv and rv["target_key"] == 35 and file_content:match("No key set") then
    print("No key is set in the file. Exiting the script.")
    return -- Exit the script
end

if rv and rv["target_key"] == 35 then
       local file = io.open(key_file_path, "r")
    local pkey

    if file then
        -- Read the key from the file (assuming the key is on the first line)
        local key_with_suffix = file:read("*l")
        file:close()

        -- Modify the pattern to capture the key and include "m" if it's minor
        pkey = key_with_suffix:match("^(%a#?b?m?)")
    end

    -- Print the extracted key to verify
    print("Extracted Key:", pkey)

    -- Prepare a lookup table to match keys to numbers
    local key_to_number = {
        ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
        ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
        ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
        ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
        ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
        ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34
    }

    -- Look up the extracted key in the table to get the number
    local selected_number = key_to_number[pkey]

    if selected_number then
        print("Matched Key Number:", selected_number)
        -- Use `selected_number` for your transposition logic or any further steps
    else
        print("Error: The extracted key does not match any known key.")
    end

    -- Map the numeric value back to the corresponding key string
 target_key = number_to_key[selected_number]

-- Define a mapping of musical keys to their corresponding note values (semitones)
key_to_semitone = {
    C = 0, ["C#"] = 1, Db = 1, D = 2, ["D#"] = 3, Eb = 3,
    E = 4, F = 5, ["F#"] = 6, Gb = 6, G = 7, ["G#"] = 8, Ab = 8,
    A = 9, ["A#"] = 10, Bb = 10, B = 11,
    Am = 9, ["A#m"] = 10, Bbm = 10, Bm = 11, Cm = 0, ["C#m"] = 1,
    Dbm = 1, Dm = 2, ["D#m"] = 3, Ebm = 3, Em = 4, Fm = 5,
    ["F#m"] = 6, Gbm = 6, Gm = 7, ["G#m"] = 8, Abm = 8
}
end




if rv and rv["target_key"] ~= 35 then
   -- Get the selected target key's numeric value from the dialog
 selected_number = rv.target_key
 -- Map the numeric value back to the corresponding key string
 target_key = number_to_key[selected_number]

-- Define a mapping of musical keys to their corresponding note values (semitones)
key_to_semitone = {
    C = 0, ["C#"] = 1, Db = 1, D = 2, ["D#"] = 3, Eb = 3,
    E = 4, F = 5, ["F#"] = 6, Gb = 6, G = 7, ["G#"] = 8, Ab = 8,
    A = 9, ["A#"] = 10, Bb = 10, B = 11,
    Am = 9, ["A#m"] = 10, Bbm = 10, Bm = 11, Cm = 0, ["C#m"] = 1,
    Dbm = 1, Dm = 2, ["D#m"] = 3, Ebm = 3, Em = 4, Fm = 5,
    ["F#m"] = 6, Gbm = 6, Gm = 7, ["G#m"] = 8, Abm = 8
}
end





-- Exit if dialog is canceled or closed
if not rv then
    print("Dialog canceled or closed.")
    return

end





-- Pattern to capture only the key part
local key_only = dkey:match("^[A-G][#b]?m?")

print("Key only:", key_only)
 detected_key = key_only

 print("detected is "..key_only)




-- Function to calculate the semitone shift between two keys
function semitone_shift(detected_key, target_key)
    -- Get the semitone values for the detected and target keys
     detected_semitone = key_to_semitone[detected_key]
     target_semitone = key_to_semitone[target_key]

    if detected_semitone == nil or target_semitone == nil then
        print("Invalid key. Please enter a valid key.")
        return
    end

    -- Calculate the semitone difference
     semitone_difference = target_semitone - detected_semitone

    -- Print the result
    if semitone_difference > 0 then
        print("Go up " .. semitone_difference .. " semitone(s) to reach " .. target_key .. ".")
    elseif semitone_difference < 0 then
        print("Go down " .. math.abs(semitone_difference) .. " semitone(s) to reach " .. target_key .. ".")
    else
        print("The detected key is already in " .. target_key .. ".")
    end
end

	if cname == true then

	function formatKey(target_key)
    local formatted_key = target_key

    -- Check if fkey is major and remove " Major"
    if formatted_key:match("Major$") then
        formatted_key = formatted_key:gsub(" Major$", "")
    -- Check if fkey is minor and replace " minor" with "m"
    elseif formatted_key:match("minor$") then
        formatted_key = formatted_key:gsub(" minor$", "m")
    end

    target_key = (formatKey(fkey))

    return formatted_key
end

  rn = rn:gsub("key_" .. fkey:match("([A-G][#b]?m?)"), "")
    print("Filename after removing key pattern:", rn)
    audio_region:set_name(rn.."-key_"..target_key)
--end



semitone_shift(detected_key, target_key)


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

	-- Function to calculate the ratio for changing pitch by a number of semitones
function calculate_ratio(semitones)
    -- Ratio calculation formula: 2^(semitones / 12)
    local ratio = 2^(semitones / 12)
    return ratio
end

-- Example usage
local semitones = semitone_difference -- Change this value to test with different semitone shifts
print (semitones)
local ratio = calculate_ratio(semitones)



-- Print the result
print("For a shift of " .. semitones .. " semitones, the ratio is: " .. ratio)


print(type(ratio))


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
		local pdialog = LuaDialog.ProgressWindow ("Transpose Audio", true)
		-- progress dialog callbacks
		function vamp_callback (_, pos)
			return pdialog:progress (pos / max_pos, "Analyzing")
		end
		function rb_progress (_, pos)
			return pdialog:progress (pos / max_pos, "Transposing")
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
		rb:set_strech_and_pitch (1, ratio) -- no overall stretching, but pitch shifting
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
    end end
