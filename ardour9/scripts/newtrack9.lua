ardour {
	["type"] = "EditorAction",
	name = "New Track - Dialog Menu",
	author      = "Justin Ehrlichman",
description = [[
Brings up a dialog menu to select track types based on templates
]]
}

function factory () return function (signal, ...)
local dialog_options = {
  {
    type = "dropdown", key = "dropdown", title = "Choose Track", values = {
      ["Choose a track Type"] = 1,
      ["Help"] = {
        ["How to use Drum Tracks"] = "drhelp",
        ["How to use Software Instruments"] = "insthelp",
        ["How to use Audio Recording"] = "audiohelp",
        ["How to use Guitar/Bass Recording"] = "guitarhelp",
        ["How to use Session Players"] = "sessionhelp",
        ["How to use Generators"] = "genhelp",
        ["Reference Materials"] = {
          ["Circle of Fifths"] = "cofhelp"
        }
      },
      ["Drummer"] = {
        ["Red Zepplin (AVL Drumkits)"] = "rz",
        ["Black Pearl (AVL Drumkits)"] = "bp",
        ["Blonde Bop (AVL Drumkits)"] = "bo",
        ["Standard Drums (ACE Fluid Synth)"] = "std",
        ["Standard 2 Drums (ACE Fluid Synth)"] = "st2",
        ["Electronic Drums (ACE Fluid SYnth)"] = "eld",
        ["Room Drums (ACE Fluid Synth)"] = "rmd",
        ["Power Drums (ACE Fluid Synth)"] = "pwd",
        ["Dance Drums (ACE Fluid Synth)"] = "dad",
        ["Jazz Drums (ACE Fluid Synth)"] = "jzd",
        ["808/809 Drums (ACE Fluid Synth)"] = "808",
        ["Brush Drums (ACE Fluid Synth)"] = "brd",
        ["Orchestral Perc (ACE Fluid Synth)"] = "orp",
        ["SoniNeko Drums (ACE Fluid Synth)"] = "son",
        ["Alesis Drumkits (Use C1 to change kits) (ACE Fluid Synth)"] = "al",
        ["Buskman's Holiday Percussion (AVL Drumkits)"] = "bus",
        ["Blonde Bop HotRod Drumkit (AVL Drumkits)"] = "hot",
        ["NIN Drumkit (ACE Fluid Synth)"] = "nin",
         ["Muldjord (ACE Fluid Synth)"] = "mj",
           ["HouseKit (ACE Fluid Synth)"] = "house",
           ["PowerKit2 (ACE Fluid Synth)"] = "pk2",
           ["Standard3 (ACE Fluid Synth)"] = "std3",
            ["AnalogT9Kit (ACE Fluid Synth)"] = "at9",
            ["AnalogT8Kit (ACE Fluid Synth)"] = "at8",
        ["Step Sequencing"] = {
          ["Red Zepplin"] = "steprz",
          ["Black Pearl Drumkit"] = "stepblack",
          ["Blonde Bop"] = "stepblond",
          ["Standard Drums"] = "stepstd",
          ["Standard 2 Drums"] = "stepst2",
          ["Electronic Drums"] = "stepel",
          ["Room Drums"] = "steproom",
          ["Power Drums"] = "steppower",
          ["Dance Drums"] = "stepdance",
          ["Jazz Drums"] = "stepjazz",
          ["808/809 Drums"] = "step808",
          ["Brush Drums"] = "stepbrush",
          ["Orchestral Perc"] = "steporch",
          ["SoniNeko Drums"] = "stepson",
          ["Buskman's Holiday Percussion"] = "stepbusk",
          ["Alesis Drumkits (Use C1 to change kits)"] = "stepal",
          ["Blonde Bop HotRod Drumkit"] = "stephot",
          ["NIN Drumkit"] = "stepnin",
          ["Muldjord"] = "stepmj",
          ["HouseKit"] = "stephouse",
            ["PowerKit2"] = "steppk2",
             ["Standard3"] = "stepstd3",
             ["AnalogT9Kit"] = "stepat9",
              ["AnalogT8Kit"] = "stepat8",
        }
      },
      ["Play Software Instruments"] = {
        ["ACE Fluid (Traditional Instruments)"] = "ac",
        ["Yoshimi (Traditional Synth)"] = "za",
        ["Surge XT (Synth with a LOT of presets)"] = "st",
        ["Samplv1 Sampler"] = "samp"
      },
      ["Session Player"] = {
        ["ACE Fluid (Traditional Instruments)"] = "acs",
        ["Yoshimi (Traditional Synth)"] = "zas",
        ["Surge XT (Synth with a LOT of presets)"] = "sts"
      },
      ["Record Audio"] = {
        ["Vocals"] = {
          ["Classic"] = "clv",
          ["Bright"] = "brv",
          ["Compressed"] = "cov",
          ["Telephone"] = "tlv",
          ["Dance"] = "dav",
          ["Natural"] = "nav",
          ["Edge"] = "edv",
          ["Fuzz"] = "fzv",
          ["Tube Vocals"] = "tub",
          ["Deeper Vocals"] = "dp",
          ["Robot Vocals"] = "rob"
        },
        ["Blank Audio Track"] = "audio"
      },
      ["Record Guitar or Bass"] = {
        ["Guitarix"] = "gx",
        ["Ratatouille"] = "ra"
      },
      ["Generators"] = {
        ["Random Chord Generator"] = {
          ["ACE Fluid Synth"] = "fluchord",
          ["Surge XT"] = "surgechord",
          ["Yoshimi"] = "yoshchord",

        },
        ["Bassline Generator"] = "bassline_gen",
        ["Melody Generator"] = {
          ["ACE Fluid Synth"] = "flumelody",
          ["Yoshimi"] = "yoshmelody",
          ["Surge XT"] = "surgemelody"
        }
      }
    },
    default = "Choose a track type"
  }
}



	-- Fetch the user config directory for the running Ardour version
local user_config_directory = ARDOUR.user_config_directory(-1)





-- Define the subdirectory you want to concatenate
local subdir = "route_templates"

-- Concatenate the config directory with the subdirectory
local full_path = user_config_directory .. "/" .. subdir

local function open_url_in_browser(url)
    -- Create the command with the given URL
    local command = "xdg-open " .. url

    -- Create a temporary file to store the command
    local file = io.open("yt.sh", "w")

    if not file then
        print("Error: Failed to create file 'yt.sh'")
    else
        -- Write the command to the file
        file:write(command .. "\n")
        file:close()
        print("File 'yt.sh' created successfully!")
    end

    -- Move the script to a temporary location and execute it
    os.execute("mv yt.sh /tmp/yt.sh")
   -- os.execute("/bin/bash /tmp/yt.sh")
    os.forkexec("/bin/bash", "/tmp/yt.sh")
end

local function find_newest_route(track_name)
	local escaped_name = track_name:gsub("(%W)", "%%%1")
	local function route_matches(route_name)
		if route_name == track_name then
			return true
		end
		-- Ardour appends .1, .2, ... when the track name already exists
		return route_name:match("^" .. escaped_name .. "%.%d+$") ~= nil
	end

	local found = nil
	for route in Session:get_routes():iter() do
		if route_matches(route:name()) then
			found = route
		end
	end
	return found
end


local function select_route(route)
	if not route or route:isnil() then
		return false
	end

	local rtav = Editor:rtav_from_route(route)
	if not rtav then
		print("Could not find the editor view for " .. route:name())
		return false
	end

	-- Selection::add only accepts region views and control points. A track view
	-- passed to set_selection aborts with "unknown selectable type".
	Editor:access_action("Mixer", "select-none")

	local guard = 0
	local limit = 0
	for _ in Session:get_routes():iter() do
		limit = limit + 1
	end
	while not route:is_selected() and guard < limit do
		Editor:access_action("Editor", "select-next-route")
		guard = guard + 1
	end

	local sel = Editor:get_selection()
	local sel_size = 0
	if sel and (not sel:empty()) and (not sel.tracks:routelist():empty()) then
		sel_size = sel.tracks:routelist():size()
	end
	if sel_size == 0 then
		return false
	end
	return route:is_selected() and sel_size == 1
end

local function add_track_from_template(template_path, track_name)
	Session:new_route_from_template(1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	local route = find_newest_route(track_name)
	if not route then
		print("Created track was not found: " .. track_name)
		return nil
	end
	if not select_route(route) then
		print("Could not select " .. track_name)
	end
	return route
end

local function import_midi_into_route(midi_path, route)
	if not midi_path or midi_path == "" then
		print("No MIDI file to import")
		return
	end
	if not route or route:isnil() then
		print("Could not find a MIDI track to import into")
		return
	end

	local midi_file = io.open(midi_path, "r")
	if not midi_file then
		print("MIDI file not found: " .. midi_path)
		return
	end
	midi_file:close()

	local tr = route:to_track()
	if not tr or tr:isnil() or tr:to_midi_track():isnil() then
		print("Track is not a MIDI track: " .. route:name())
		return
	end

	if not select_route(route) then
		print("Could not select " .. route:name() .. ", MIDI import skipped")
		return
	end

	local sel = Editor:get_selection()
	if sel:empty() or sel.tracks:routelist():empty() or sel.tracks:routelist():size() ~= 1 then
		print("Could not select " .. route:name() .. ", MIDI import skipped")
		return
	end

	-- Ardour 8.12 aborts when do_import sees a file path that is already a
	-- session source, so that version imports a unique copy. On Ardour 9 a
	-- copied file crashes inside the import, so the original path is used.
	local import_path = midi_path
	local temp_copy = nil
	local revision = ""
	pcall(function() revision = tostring(ARDOUR.revision) end)
	if revision:match("^8%.") then
		temp_copy = string.format("/tmp/la-midi-%d-%d.mid", os.time(), math.floor((os.clock() or 0) * 1000000) % 1000000)
		if os.execute("cp " .. string.format("%q", midi_path) .. " " .. string.format("%q", temp_copy)) then
			import_path = temp_copy
		end
	end

	local files = C.StringVector()
	files:push_back(import_path)
	local pos = Temporal.timepos_t(0)
	Editor:do_import(files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), tr, false)
	if temp_copy and import_path == temp_copy then
		os.remove(import_path)
	end
end

local function rename_melody_region(route, name)
	if not route or route:isnil() or not name or name == "" then
		return
	end
	local tr = route:to_track()
	if not tr or tr:isnil() then
		return
	end
	local playlist = tr:playlist()
	if not playlist or playlist:isnil() then
		return
	end
	for region in playlist:region_list():iter() do
		region:set_name(name)
	end
end

local function import_midi_into_track(midi_path, track_name)
	local route = find_newest_route(track_name)
	if not route then
		print("Could not find a MIDI track named " .. track_name .. " to import into")
		return
	end
	import_midi_into_route(midi_path, route)
end

local function create_seq(stemplate_path, strack_name, template_path, track_name)
  -- Create the first route from the specified template and track name
  add_track_from_template(stemplate_path, strack_name)

  -- Get the selection and print track names
  local sel = Editor:get_selection()
  for r in sel.tracks:routelist():iter() do
    the_name = r:name()
    print(the_name)
  end

  -- Create the second route from the specified template and track name
  add_track_from_template(template_path, track_name)

  -- Get the selection again and connect MIDI input ports
  sel = Editor:get_selection()
  for r in sel.tracks:routelist():iter() do
    if not r:to_track():isnil() and not r:to_track():to_midi_track():isnil() then
      local inputmidiport = r:input():midi(0)
      inputmidiport:connect(the_name .. "/midi_out 1")
    end
  end
end

local function generate_melody(template_path, track_name, open_soundfont)
	print("You picked Melody Generator: " .. track_name)

	local route = add_track_from_template(template_path, track_name)

	local function open_font()
		if not open_soundfont or not route or route:isnil() then
			return
		end
		select_route(route)
		Editor:access_action("LuaAction", "script-15")
	end

	local sespath = Session:path()
	local key_file_path = sespath .. "/key.txt"

	local file = io.open(key_file_path, "r")
	local file_content = "No key set"

	if file then
		file_content = file:read("*a")
		file:close()
	else
		print("Warning: Could not open file for reading at " .. key_file_path)
	end

	local genres_path = "/opt/LogicalArdour/genres.json"
	local genres_file = io.open(genres_path, "r")
	if not genres_file then
		print("Could not open " .. genres_path)
		LuaDialog.Message("Melody Generator", "Could not open " .. genres_path, LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
		open_font()
		return
	end
	local genres_content = genres_file:read("*a")
	genres_file:close()

	local genre_values = {}
	local genre_by_index = {}
	local genre_name_by_index = {}
	local genre_index = 0
	local default_genre = nil
	for id, name in genres_content:gmatch('"id"%s*:%s*"([^"]+)"%s*,%s*"displayName"%s*:%s*"([^"]+)"') do
		genre_index = genre_index + 1
		genre_values[name] = genre_index
		genre_by_index[genre_index] = id
		genre_name_by_index[genre_index] = name
		if not default_genre then
			default_genre = name
		end
		if name == "Pop" then
			default_genre = name
		end
	end
	if genre_index == 0 then
		LuaDialog.Message("Melody Generator", "No genres found in " .. genres_path, LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
		open_font()
		return
	end

	local scurrent_key_option = "Set to current project key: " .. file_content
	local sdialog_options = {
		{
			type = "dropdown",
			key = "target_key",
			title = "Choose the key you want the session player to follow",
			values = {
				["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
				["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
				["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
				["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
				["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
				["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
				[scurrent_key_option] = 35,
				["Do not change key"] = 36
			},
			default = scurrent_key_option
		},
		{
			type = "dropdown",
			key = "genre",
			title = "Genre",
			values = genre_values,
			default = default_genre
		},
		{
			type = "entry",
			key = "bars",
			title = "Number of bars",
			default = "4"
		}
	}

	local reverse_lookup = {}
	for skey, value in pairs(sdialog_options[1].values) do
		reverse_lookup[value] = skey
	end

	local sod = LuaDialog.Dialog("Choose Target Key", sdialog_options)
	local srv = sod:run()

	if not srv then
		print("Dialog was canceled.")
		open_font()
		return
	end

	local selected_key_value = srv["target_key"]
	local skey = reverse_lookup[selected_key_value]
	local scale = ""

	if selected_key_value == 35 then
		if file_content:match("No key set") then
			print("No key is set in the file. Exiting the script.")
			open_font()
			return
		end
		skey = file_content:match("^%a#?b?m?")
	end

	if skey:find("m") then
		scale = "minor"
	else
		scale = "major"
	end

	print("Key: " .. skey .. " Scale: " .. scale)

	if skey:sub(-1) == "m" then
		skey = skey:sub(1, -2)
	end

	print("Key without 'm': " .. skey)
	local desired_key = skey

	local genre_choice = tonumber(srv["genre"]) or srv["genre"]
	local genre_id = genre_by_index[genre_choice]
	local genre_name = genre_name_by_index[genre_choice]
	if not genre_id then
		LuaDialog.Message("Melody Generator", "No genre selected.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
		open_font()
		return
	end

	local bar_count = tonumber(srv["bars"])
	if not bar_count or bar_count < 1 or bar_count ~= math.floor(bar_count) then
		LuaDialog.Message("Melody Generator", "Number of bars must be a whole number of at least 1.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
		open_font()
		return
	end
	bar_count = math.floor(bar_count)
	print("Genre: " .. genre_id .. " Bars: " .. bar_count)

	local tm = Temporal.TempoMap.read()
	local tempo = tm:tempo_at(Temporal.timepos_t(0))
	local bpm = math.floor(tempo:note_types_per_minute() + 0.5)

	local filepath = "/tmp/melody" .. desired_key .. scale .. ".mid"
	local quotedfilepath = '"' .. filepath .. '"'

	local command = "/opt/LogicalArdour/melody_generator --key \""
		.. desired_key .. "\" --scale " .. scale .. " --genre \"" .. genre_id
		.. "\" --bars " .. bar_count .. " --tempo " .. bpm
		.. " --output " .. quotedfilepath

	local handle = io.popen(command .. " 2>&1")
	local output = ""
	if handle then
		output = handle:read("*a") or ""
		handle:close()
	else
		os.execute(command)
	end
	if output ~= "" then
		print(output)
	end
	local resolved_scale = output:match("Resolved scale: (%S+)") or scale
	local region_name = genre_name .. " " .. desired_key .. " " .. resolved_scale

	import_midi_into_route(filepath, route)
	rename_melody_region(route, region_name)
	open_font()

	os.execute("rm -rf " .. quotedfilepath)
end

	local od = LuaDialog.Dialog ("Choose Track", dialog_options)
	local rv = od:run()

	    	if rv and rv["dropdown"] == "bassline_gen" then
		print("You picked Bassline Generator")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/Bassline.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Bassline"

		add_track_from_template(template_path, track_name)
local sespath = Session:path()
local key_file_path = sespath .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

local scurrent_key_option = "Set to current project key: " .. file_content
local sdialog_options = {
  {
    type = "dropdown",
    key = "target_key",
    title = "Choose the key you want the session player to follow",
    values = {
      ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
      ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
      ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
      ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
      ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
      ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
      [scurrent_key_option] = 35,
      ["Do not change key"] = 36
    },
    default = scurrent_key_option
  }
}

local reverse_lookup = {}
for skey, value in pairs(sdialog_options[1].values) do
  reverse_lookup[value] = skey
end

-- Create and run the dialog
local sod = LuaDialog.Dialog("Choose Target Key", sdialog_options)
local srv = sod:run()

-- Exit if dialog is canceled
if not srv then
  print("Dialog was canceled.")
  return
end

local selected_key_value = srv["target_key"]
local skey = reverse_lookup[selected_key_value] -- Get the key name from the value
local scale = ""

-- Handle "Set to current project key"
if selected_key_value == 35 then
  if file_content:match("No key set") then
    print("No key is set in the file. Exiting the script.")
    return -- Exit the script
  end
  skey = file_content:match("^%a#?b?m?") -- Extract the key
end

-- Determine scale (major or minor)
if skey:find("m") then
  scale = "minor"
else
  scale = "major"
end

--scale = scale:sub(1, 1):upper() .. scale:sub(2)

-- Print the result
print("Key: " .. skey .. " Scale: " .. scale)

if skey:sub(-1) == "m" then
  skey = skey:sub(1, -2) -- Extract everything except the last character
end

-- Print the result
print("Key without 'm': " .. skey)
-- Define the key to search for
 desired_key = skey -- Change this to the desired key (e.g., "A", "Ab", "A#")



    local filepath = "/tmp/bassline"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/bassline_generator " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

import_midi_into_track(filepath, track_name)

			local delete_file = "rm -rf "..filepath

os.execute(delete_file)
end

	if rv and rv["dropdown"] == "flumelody" then
		generate_melody(full_path .. "/Fluid.template", "Ace Fluid Synth", true)
		return
	end

	if rv and rv["dropdown"] == "yoshmelody" then
		generate_melody(full_path .. "/Yoshimi.template", "Yoshimi", false)
		return
	end

	if rv and rv["dropdown"] == "surgemelody" then
		generate_melody(full_path .. "/Surge XT.template", "Surge XT", false)
		return
	end

	if rv and rv["dropdown"] == "rz" then
		print("You picked Red Zepplin Drumkit")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/red zepplin.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Red Zepplin Drumkit"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)

	end

		if rv and rv["dropdown"] == "pk2" then
		print("You picked Red Zepplin Drumkit")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/powerkit2.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "PowerKit2"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)

	end

			if rv and rv["dropdown"] == "std3" then
		print("You picked Standard 3 Kit")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/standard3.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Standard3kit"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)

	end


			if rv and rv["dropdown"] == "at9" then
		print("You picked AnalogT9Kit")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/at9.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "AnalogT9Kit"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)

	end


			if rv and rv["dropdown"] == "at8" then
		print("You picked AnalogT8Kit")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/at8.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "AnalogT8Kit"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)

	end



	if rv and rv["dropdown"] == "bp" then
		print("You picked Black Pearl")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/Black Pearl Drumkit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Black Pearl Drumkit"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)

	end

		if rv and rv["dropdown"] == "nin" then
		print("You picked NIN Drunkit")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/NIN Drumkit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "NIN Drumkit"

		add_track_from_template(template_path, track_name)
				import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)

	end





	if rv and rv["dropdown"] == "bo" then
		print("blond bop")
		-- Replace the path below with the path to your track template
		--local template_path = "/home/jman/templates/Blonde Bop Drumkit.template"

		local template_path = full_path .. "/Blonde Bop Drumkit.template"


		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Blonde Bop Drumkit"

		add_track_from_template(template_path, track_name)
				import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

		if rv and rv["dropdown"] == "house" then
		print("blond bop")
		-- Replace the path below with the path to your track template
		--local template_path = "/home/jman/templates/Blonde Bop Drumkit.template"

		local template_path = full_path .. "/HouseKit.template"


		-- Replace "Track Name" with the name you want for your new track
		local track_name = "HouseKit"

		add_track_from_template(template_path, track_name)
				import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end


		if rv and rv["dropdown"] == "ac" then
		print("Ace Fluid Synth")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Fluid.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ace Fluid Synth"

		add_track_from_template(template_path, track_name)
		Editor:access_action("LuaAction", "script-15")
		return  -- stop further processing
	end

			if rv and rv["dropdown"] == "za" then
		print("Yoshimi")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Yoshimi.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Yoshimi"

		add_track_from_template(template_path, track_name)
	end

			if rv and rv["dropdown"] == "st" then
		print("Surge XT")
		-- Replace the path below with the path to your track template
		-- local template_path = "/home/jman/templates/Surge XT.template"
		 local template_path = full_path .. "/Surge XT.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Surge XT"

		add_track_from_template(template_path, track_name)
	end

				if rv and rv["dropdown"] == "ra" then
		print("NAM")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Ratatouille.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ratatouille"

		add_track_from_template(template_path, track_name)
	end

					if rv and rv["dropdown"] == "gx" then
		print("Gutiarix")


		-- Replace the path below with the path to your track template
		  local template_path = full_path .. "/Guitarix.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Guitarix"

		add_track_from_template(template_path, track_name)
	end

						if rv and rv["dropdown"] == "clv" then
		print("Classic Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/classic.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "classic"

		add_track_from_template(template_path, track_name)
	end

						if rv and rv["dropdown"] == "brv" then
		print("Bright Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/bright.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "bright"

		add_track_from_template(template_path, track_name)
	end

						if rv and rv["dropdown"] == "cov" then
		print("Compressed Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/compressed.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "compressed"

		add_track_from_template(template_path, track_name)
	end


						if rv and rv["dropdown"] == "tlv" then
		print("telephone Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/telephone.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "telephone"

		add_track_from_template(template_path, track_name)
	end


						if rv and rv["dropdown"] == "dav" then
		print("Dance Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/dance.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "dance"

		add_track_from_template(template_path, track_name)
	end

							if rv and rv["dropdown"] == "nav" then
		print("Natural Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/natural.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "natural"

		add_track_from_template(template_path, track_name)
	end

		if rv and rv["dropdown"] == "std" then
		print("Standard Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Standard Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Standard Drums"

		add_track_from_template(template_path, track_name)
				import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end
			if rv and rv["dropdown"] == "mj" then
		print("Drumlabooh")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/muldjord.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Muldjord Kit"

		add_track_from_template(template_path, track_name)
				import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end


	if rv and rv["dropdown"] == "st2" then
		print("Standard 2 Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Standard 2 Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Standard 2 Drums"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

		if rv and rv["dropdown"] == "eld" then
		print("Electronic Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Electronic Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Electronic Drums"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end


		if rv and rv["dropdown"] == "rmd" then
		print("Room Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Room Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Room Drums"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

			if rv and rv["dropdown"] == "pwd" then
		print("Power Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Power Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Power Drums"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

			if rv and rv["dropdown"] == "dad" then
		print("Dance Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Dance Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Dance Drums"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

			if rv and rv["dropdown"] == "jzd" then
		print("Dance Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Jazz Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Jazz Drums"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

			if rv and rv["dropdown"] == "acs" then
		print("Ace Fluid Synth")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/GM Session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ace Fluid Synth Session"

		add_track_from_template(template_path, track_name)
local sespath = Session:path()
local key_file_path = sespath .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

local scurrent_key_option = "Set to current project key: " .. file_content
local sdialog_options = {
  {
    type = "dropdown",
    key = "target_key",
    title = "Choose the key you want the session player to follow",
    values = {
      ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
      ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
      ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
      ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
      ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
      ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
      [scurrent_key_option] = 35,
      ["Do not change key"] = 36
    },
    default = scurrent_key_option
  }
}

local reverse_lookup = {}
for skey, value in pairs(sdialog_options[1].values) do
  reverse_lookup[value] = skey
end

-- Create and run the dialog
local sod = LuaDialog.Dialog("Choose Target Key", sdialog_options)
local srv = sod:run()

-- Exit if dialog is canceled
if not srv then
  print("Dialog was canceled.")
  return
end

local selected_key_value = srv["target_key"]
local skey = reverse_lookup[selected_key_value] -- Get the key name from the value
local scale = ""

-- Handle "Set to current project key"
if selected_key_value == 35 then
  if file_content:match("No key set") then
    print("No key is set in the file. Exiting the script.")
    return -- Exit the script
  end
  skey = file_content:match("^%a#?b?m?") -- Extract the key
end

-- Determine scale (major or minor)
if skey:find("m") then
  scale = "minor"
else
  scale = "major"
end

scale = scale:sub(1, 1):upper() .. scale:sub(2)

-- Print the result
print("Key: " .. skey .. " Scale: " .. scale)

if skey:sub(-1) == "m" then
  skey = skey:sub(1, -2) -- Extract everything except the last character
end

-- Print the result
print("Key without 'm': " .. skey)
-- Define the key to search for
 desired_key = skey -- Change this to the desired key (e.g., "A", "Ab", "A#")

-- Define the directory containing the chord progressions
 directory = "/opt/LogicalArdour/Drum loops, chords, and chord progressions/MIDI Progressions/"..scale.."/"

-- Function to get files in a directory
function get_files_in_directory(dir)
    local files = {}
    for file in io.popen('ls "' .. dir .. '"'):lines() do
        if file:match("%.mid$") then -- Check if the file ends with .mid
            table.insert(files, file)
        end
    end
    return files
end

-- Function to filter files by key
function filter_files_by_key(files, fkey)
    local filtered_files = {}
    for _, file in ipairs(files) do
        -- Match files that start with the exact key followed by a non-word character or `.mid`
        if file:match("^" .. fkey .. "[%W_]") or file:match("^" .. fkey .. "%.mid$") then
            table.insert(filtered_files, file)
        end
    end
    return filtered_files
end

-- Function to pick a random file
function pick_random_file(files)
    if #files == 0 then
        return nil -- No files matched
    end
    math.randomseed(os.time()) -- Seed the random number generator
    local random_index = math.random(1, #files)
    return files[random_index]
end

-- Main logic
local all_files = get_files_in_directory(directory)

local matching_files = filter_files_by_key(all_files, desired_key)

local random_file = pick_random_file(matching_files)

if random_file then
    print("Random progression in key " .. desired_key .. ": " .. random_file)
    local full_file_path = directory .. random_file
	import_midi_into_track(full_file_path, track_name)
else
    print("No progressions found for key: " .. desired_key)
 scale = scale:sub(1, 1):lower() .. scale:sub(2)

    local filepath = "/tmp/chord"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/newchord " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

import_midi_into_track(filepath, track_name)

			local delete_file = "rm -rf "..filepath

os.execute(delete_file)
end end
		if rv and rv["dropdown"] == "zas" then
		print("Yoshimi")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Yosh Session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Yoshimi Session"

		add_track_from_template(template_path, track_name)
	local sespath = Session:path()
local key_file_path = sespath .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

local scurrent_key_option = "Set to current project key: " .. file_content
local sdialog_options = {
  {
    type = "dropdown",
    key = "target_key",
    title = "Choose the key you want the session player to follow",
    values = {
      ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
      ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
      ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
      ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
      ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
      ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
      [scurrent_key_option] = 35,
      ["Do not change key"] = 36
    },
    default = scurrent_key_option
  }
}

local reverse_lookup = {}
for skey, value in pairs(sdialog_options[1].values) do
  reverse_lookup[value] = skey
end

-- Create and run the dialog
local sod = LuaDialog.Dialog("Choose Target Key", sdialog_options)
local srv = sod:run()

-- Exit if dialog is canceled
if not srv then
  print("Dialog was canceled.")
  return
end

local selected_key_value = srv["target_key"]
local skey = reverse_lookup[selected_key_value] -- Get the key name from the value
local scale = ""

-- Handle "Set to current project key"
if selected_key_value == 35 then
  if file_content:match("No key set") then
    print("No key is set in the file. Exiting the script.")
    return -- Exit the script
  end
  skey = file_content:match("^%a#?b?m?") -- Extract the key
end

-- Determine scale (major or minor)
if skey:find("m") then
  scale = "minor"
else
  scale = "major"
end

scale = scale:sub(1, 1):upper() .. scale:sub(2)

-- Print the result
print("Key: " .. skey .. " Scale: " .. scale)

if skey:sub(-1) == "m" then
  skey = skey:sub(1, -2) -- Extract everything except the last character
end

-- Print the result
print("Key without 'm': " .. skey)
-- Define the key to search for
 desired_key = skey -- Change this to the desired key (e.g., "A", "Ab", "A#")

-- Define the directory containing the chord progressions
 directory = "/opt/LogicalArdour/Drum loops, chords, and chord progressions/MIDI Progressions/"..scale.."/"

-- Function to get files in a directory
function get_files_in_directory(dir)
    local files = {}
    for file in io.popen('ls "' .. dir .. '"'):lines() do
        if file:match("%.mid$") then -- Check if the file ends with .mid
            table.insert(files, file)
        end
    end
    return files
end

-- Function to filter files by key
function filter_files_by_key(files, fkey)
    local filtered_files = {}
    for _, file in ipairs(files) do
        -- Match files that start with the exact key followed by a non-word character or `.mid`
        if file:match("^" .. fkey .. "[%W_]") or file:match("^" .. fkey .. "%.mid$") then
            table.insert(filtered_files, file)
        end
    end
    return filtered_files
end

-- Function to pick a random file
function pick_random_file(files)
    if #files == 0 then
        return nil -- No files matched
    end
    math.randomseed(os.time()) -- Seed the random number generator
    local random_index = math.random(1, #files)
    return files[random_index]
end

-- Main logic
local all_files = get_files_in_directory(directory)

local matching_files = filter_files_by_key(all_files, desired_key)

local random_file = pick_random_file(matching_files)

if random_file then
    print("Random progression in key " .. desired_key .. ": " .. random_file)
    local full_file_path = directory .. random_file
	import_midi_into_track(full_file_path, track_name)
else
    print("No progressions found for key: " .. desired_key)
 scale = scale:sub(1, 1):lower() .. scale:sub(2)

    local filepath = "/tmp/chord"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/newchord " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

import_midi_into_track(filepath, track_name)

			local delete_file = "rm -rf "..filepath

os.execute(delete_file)
end end
		if rv and rv["dropdown"] == "sts" then
		print("Surge XT")
		-- Replace the path below with the path to your track template
		-- local template_path = "/home/jman/templates/Surge XT.template"
		 local template_path = full_path .. "/Surge XT Session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Surge XT Session"

		add_track_from_template(template_path, track_name)
		local sespath = Session:path()
		local key_file_path = sespath .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

local scurrent_key_option = "Set to current project key: " .. file_content
local sdialog_options = {
  {
    type = "dropdown",
    key = "target_key",
    title = "Choose the key you want the session player to follow",
    values = {
      ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
      ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
      ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
      ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
      ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
      ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
      [scurrent_key_option] = 35,
      ["Do not change key"] = 36
    },
    default = scurrent_key_option
  }
}

local reverse_lookup = {}
for skey, value in pairs(sdialog_options[1].values) do
  reverse_lookup[value] = skey
end

-- Create and run the dialog
local sod = LuaDialog.Dialog("Choose Target Key", sdialog_options)
local srv = sod:run()

-- Exit if dialog is canceled
if not srv then
  print("Dialog was canceled.")
  return
end

local selected_key_value = srv["target_key"]
local skey = reverse_lookup[selected_key_value] -- Get the key name from the value
local scale = ""

-- Handle "Set to current project key"
if selected_key_value == 35 then
  if file_content:match("No key set") then
    print("No key is set in the file. Exiting the script.")
    return -- Exit the script
  end
  skey = file_content:match("^%a#?b?m?") -- Extract the key
end

-- Determine scale (major or minor)
if skey:find("m") then
  scale = "minor"
else
  scale = "major"
end

scale = scale:sub(1, 1):upper() .. scale:sub(2)

-- Print the result
print("Key: " .. skey .. " Scale: " .. scale)

if skey:sub(-1) == "m" then
  skey = skey:sub(1, -2) -- Extract everything except the last character
end

-- Print the result
print("Key without 'm': " .. skey)
-- Define the key to search for
 desired_key = skey -- Change this to the desired key (e.g., "A", "Ab", "A#")

-- Define the directory containing the chord progressions
 directory = "/opt/LogicalArdour/Drum loops, chords, and chord progressions/MIDI Progressions/"..scale.."/"

-- Function to get files in a directory
function get_files_in_directory(dir)
    local files = {}
    for file in io.popen('ls "' .. dir .. '"'):lines() do
        if file:match("%.mid$") then -- Check if the file ends with .mid
            table.insert(files, file)
        end
    end
    return files
end

-- Function to filter files by key
function filter_files_by_key(files, fkey)
    local filtered_files = {}
    for _, file in ipairs(files) do
        -- Match files that start with the exact key followed by a non-word character or `.mid`
        if file:match("^" .. fkey .. "[%W_]") or file:match("^" .. fkey .. "%.mid$") then
            table.insert(filtered_files, file)
        end
    end
    return filtered_files
end

-- Function to pick a random file
function pick_random_file(files)
    if #files == 0 then
        return nil -- No files matched
    end
    math.randomseed(os.time()) -- Seed the random number generator
    local random_index = math.random(1, #files)
    return files[random_index]
end

-- Main logic
local all_files = get_files_in_directory(directory)

local matching_files = filter_files_by_key(all_files, desired_key)

local random_file = pick_random_file(matching_files)

if random_file then
    print("Random progression in key " .. desired_key .. ": " .. random_file)
    local full_file_path = directory .. random_file
	import_midi_into_track(full_file_path, track_name)
else
    print("No progressions found for key: " .. desired_key)
 scale = scale:sub(1, 1):lower() .. scale:sub(2)

    local filepath = "/tmp/chord"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/newchord " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

import_midi_into_track(filepath, track_name)



local delete_file = "rm -rf "..filepath

os.execute(delete_file)



end
	end


						if rv and rv["dropdown"] == "edv" then
		print("Edge Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Edge Vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Edge Vocals"

		add_track_from_template(template_path, track_name)
	end

							if rv and rv["dropdown"] == "fzv" then
		print("Fuzz Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Fuzz Vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Fuzz Vocals"

		add_track_from_template(template_path, track_name)
	end

							if rv and rv["dropdown"] == "808" then
		print("808 Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/808-909.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "808-809 Drums"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

								if rv and rv["dropdown"] == "drl" then
		print("808 Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/drumlabooh.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "drumlabooh"

		add_track_from_template(template_path, track_name)
	end

									if rv and rv["dropdown"] == "brd" then
		print("Brush Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Brush Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Brush Drums"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

									if rv and rv["dropdown"] == "orp" then
		print("Orchestral Perc")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Orchestral Perc.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Orchestral Perc"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

										if rv and rv["dropdown"] == "son" then
		print("SoniNeko Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/soni.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "SoniNeko Drums"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end
	if rv and rv["dropdown"] == "al" then
	print("Alesis Drumkits")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/al.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Alesis Drumkits"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

		if rv and rv["dropdown"] == "tub" then
	print("Tube Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/tube.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Tube Vocals"

		add_track_from_template(template_path, track_name)
	end

			if rv and rv["dropdown"] == "dp" then
	print("Deeper Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/deeper.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Deeper Vocals"

		add_track_from_template(template_path, track_name)
	end

			if rv and rv["dropdown"] == "rob" then
	print("Robot Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/robot vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Robot Vocals"

		add_track_from_template(template_path, track_name)
	end
		if rv and rv["dropdown"] == "audio" then
	print("Audio")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/audio.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "audio"

		add_track_from_template(template_path, track_name)
	end


			if rv and rv["dropdown"] == "rob" then
	print("Robot Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/robot vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Robot Vocals"

		add_track_from_template(template_path, track_name)
	end
		if rv and rv["dropdown"] == "samp" then
	print("Samplv1 Sampler")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/sampler.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Samplv1 Sampler"

		add_track_from_template(template_path, track_name)
	end

			if rv and rv["dropdown"] == "bus" then
	print("Buskman's Holiday Percussion")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Buskman.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Buskman's Holiday Percussion"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end
		if rv and rv["dropdown"] == "hot" then
	print("Blonde Bop HotRod Drumkit")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/hotrod.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Blonde Bop HotRod Drumkit"

		add_track_from_template(template_path, track_name)
			import_midi_into_track("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid", track_name)
	end

		if rv and rv["dropdown"] == "drhelp" then
	print("Drum Help")
open_url_in_browser("https://youtu.be/COm3ym6Y-s8")
	end

		if rv and rv["dropdown"] == "insthelp" then
	print("Software Instruments Help")
open_url_in_browser("https://youtu.be/your_software_instruments_video")
	end

		if rv and rv["dropdown"] == "audiohelp" then
	print("Audio Recording Help")
open_url_in_browser("https://youtu.be/your_audio_recording_video")
	end

		if rv and rv["dropdown"] == "guitarhelp" then
	print("Guitar/Bass Recording Help")
open_url_in_browser("https://youtu.be/your_guitar_recording_video")
	end

		if rv and rv["dropdown"] == "sessionhelp" then
	print("Session Players Help")
open_url_in_browser("https://youtu.be/your_session_players_video")
	end

		if rv and rv["dropdown"] == "genhelp" then
	print("Generators Help")
open_url_in_browser("https://youtu.be/your_generators_video")
	end

		if rv and rv["dropdown"] == "cofhelp" then
	print("Opening Circle of Fifths Reference")
open_url_in_browser("https://randscullard.com/CircleOfFifths/")
	end

		if rv and rv["dropdown"] == "steprz" then


	create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Red Zepplin",
  full_path .. "/red zepplin.template",
  "Red Zepplin"
)
end



			if rv and rv["dropdown"] == "stepblack" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Black Pearl Drumkit",
  full_path .. "/Black Pearl Drumkit.template",
  "Black Pearl"
)
	end



				if rv and rv["dropdown"] == "stepblond" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Blonde Bop Drumkit",
  full_path .. "/Blonde Bop Drumkit.template",
  "Blonde Bop"
)
	end



					if rv and rv["dropdown"] == "stepstd" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Standard Drums",
  full_path .. "/Standard Drums.template",
  "Standard Drums"
)
	end

				if rv and rv["dropdown"] == "stepst2" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Standard 2 Drums",
  full_path .. "/Standard 2 Drums.template",
  "Standard 2 Drums"
)
	end


					if rv and rv["dropdown"] == "stepel" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Electronic Drums",
  full_path .. "/Electronic Drums.template",
  "Electronic Drums"
)
	end

					if rv and rv["dropdown"] == "steproom" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Room Drums",
  full_path .. "/Room Drums.template",
  "Room Drums"
)
	end


					if rv and rv["dropdown"] == "steppower" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Power Drums",
  full_path .. "/Power Drums.template",
  "Power Drums"
)
end


					if rv and rv["dropdown"] == "stepdance" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Dance Drums",
  full_path .. "/Dance Drums.template",
  "Dance Drums"
)
end



					if rv and rv["dropdown"] == "stepjazz" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Jazz Drums",
  full_path .. "/Jazz Drums.template",
  "Jazz Drums"
)
end


					if rv and rv["dropdown"] == "step808" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-808-909 Drums",
  full_path .. "/808-909.template",
  "808-909 Drums"
)
end
if rv and rv["dropdown"] == "stepbrush" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Brush Drums",
  full_path .. "/Brush Drums.template",
  "Brush Drums"
)
end


if rv and rv["dropdown"] == "steporch" then

create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Orchestral Perc",
  full_path .. "/Orchestral Perc.template",
  "Orchestral Perc"
)
end

if rv and rv["dropdown"] == "stepson" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-SoniNeko",
  full_path .. "/soni.template",
  "SoniNeko Drums"
)
end
--Buskman's Holiday Percussion
if rv and rv["dropdown"] == "stepbusk" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Buskman's Holiday Percussion",
  full_path .. "/Buskman.template",
  "Buskman's Holiday Percussion"
)
end

--/al.template  Alesis Drumkits

if rv and rv["dropdown"] == "stepal" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Alesis Drumkits",
  full_path .. "/al.template",
  "Alesis Drumkits"
)
end

if rv and rv["dropdown"] == "stephot" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Blonde Bop HotRod Kit",
  full_path .. "/hotrod.template",
  "Blonde Bop HotRod Kit"
)
end

if rv and rv["dropdown"] == "stepnin" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-NIN Drumkit",
  full_path .. "/NIN Drumkit.template",
  "NIN Drumkit"
)
end
if rv and rv["dropdown"] == "stepmj" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Muldjord",
  full_path .. "/muldjord.template",
  "Muldjord"
)
end

if rv and rv["dropdown"] == "stephouse" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-HouseKit",
  full_path .. "/HouseKit.template",
  "HouseKit"
)
end

if rv and rv["dropdown"] == "steppk2" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-PowerKit2",
  full_path .. "/powerkit2.template",
  "Powerkit2"
)
end

if rv and rv["dropdown"] == "stepstd3" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-Standard3Kit",
  full_path .. "/standard3.template",
  "Standard3Kit"
)
end
if rv and rv["dropdown"] == "stepat9" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-AnalogT9Kit",
  full_path .. "/at9.template",
  "AnalogT9Kit"
)
end

if rv and rv["dropdown"] == "stepat8" then



create_seq(
  full_path .. "/Step Sequencer.template",
  "Step Sequencer-AnalogT8Kit",
  full_path .. "/at8.template",
  "AnalogT8Kit"
)
end
			if rv and rv["dropdown"] == "fluchord" then
		print("Ace Fluid Synth")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Fluid.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Chord Generation - ACE Fluid"

		add_track_from_template(template_path, track_name)

local sespath = Session:path()
local key_file_path = sespath .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

local scurrent_key_option = "Set to current project key: " .. file_content
local sdialog_options = {
  {
    type = "dropdown",
    key = "target_key",
    title = "Choose the key you want the session player to follow",
    values = {
      ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
      ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
      ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
      ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
      ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
      ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
      [scurrent_key_option] = 35,
      ["Do not change key"] = 36
    },
    default = scurrent_key_option
  }
}

local reverse_lookup = {}
for skey, value in pairs(sdialog_options[1].values) do
  reverse_lookup[value] = skey
end

-- Create and run the dialog
local sod = LuaDialog.Dialog("Choose Target Key", sdialog_options)
local srv = sod:run()

-- Exit if dialog is canceled
if not srv then
  print("Dialog was canceled.")
  return
end

local selected_key_value = srv["target_key"]
local skey = reverse_lookup[selected_key_value] -- Get the key name from the value
local scale = ""

-- Handle "Set to current project key"
if selected_key_value == 35 then
  if file_content:match("No key set") then
    print("No key is set in the file. Exiting the script.")
    return -- Exit the script
  end
  skey = file_content:match("^%a#?b?m?") -- Extract the key
end

-- Determine scale (major or minor)
if skey:find("m") then
  scale = "minor"
else
  scale = "major"
end

scale = scale:sub(1, 1):upper() .. scale:sub(2)

-- Print the result
print("Key: " .. skey .. " Scale: " .. scale)

if skey:sub(-1) == "m" then
  skey = skey:sub(1, -2) -- Extract everything except the last character
end

-- Print the result
print("Key without 'm': " .. skey)
-- Define the key to search for
 desired_key = skey -- Change this to the desired key (e.g., "A", "Ab", "A#")

-- Define the directory containing the chord progressions
 directory = "/opt/LogicalArdour/Drum loops, chords, and chord progressions/MIDI Progressions/"..scale.."/"

-- Function to get files in a directory
function get_files_in_directory(dir)
    local files = {}
    for file in io.popen('ls "' .. dir .. '"'):lines() do
        if file:match("%.mid$") then -- Check if the file ends with .mid
            table.insert(files, file)
        end
    end
    return files
end

-- Function to filter files by key
function filter_files_by_key(files, fkey)
    local filtered_files = {}
    for _, file in ipairs(files) do
        -- Match files that start with the exact key followed by a non-word character or `.mid`
        if file:match("^" .. fkey .. "[%W_]") or file:match("^" .. fkey .. "%.mid$") then
            table.insert(filtered_files, file)
        end
    end
    return filtered_files
end

-- Function to pick a random file
function pick_random_file(files)
    if #files == 0 then
        return nil -- No files matched
    end
    math.randomseed(os.time()) -- Seed the random number generator
    local random_index = math.random(1, #files)
    return files[random_index]
end

-- Main logic
local all_files = get_files_in_directory(directory)

local matching_files = filter_files_by_key(all_files, desired_key)

local random_file = pick_random_file(matching_files)

if random_file then
    print("Random progression in key " .. desired_key .. ": " .. random_file)
    local full_file_path = directory .. random_file
	import_midi_into_track(full_file_path, track_name)
else
    print("No progressions found for key: " .. desired_key)
 scale = scale:sub(1, 1):lower() .. scale:sub(2)

    local filepath = "/tmp/chord"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/newchord " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

import_midi_into_track(filepath, track_name)

			local delete_file = "rm -rf "..filepath

os.execute(delete_file)
end end
		if rv and rv["dropdown"] == "yoshchord" then
		print("Surge XT")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Yoshimi.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Chord Generation - Yoshimi"

		add_track_from_template(template_path, track_name)
local sespath = Session:path()
local key_file_path = sespath .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

local scurrent_key_option = "Set to current project key: " .. file_content
local sdialog_options = {
  {
    type = "dropdown",
    key = "target_key",
    title = "Choose the key you want the session player to follow",
    values = {
      ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
      ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
      ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
      ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
      ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
      ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
      [scurrent_key_option] = 35,
      ["Do not change key"] = 36
    },
    default = scurrent_key_option
  }
}

local reverse_lookup = {}
for skey, value in pairs(sdialog_options[1].values) do
  reverse_lookup[value] = skey
end

-- Create and run the dialog
local sod = LuaDialog.Dialog("Choose Target Key", sdialog_options)
local srv = sod:run()

-- Exit if dialog is canceled
if not srv then
  print("Dialog was canceled.")
  return
end

local selected_key_value = srv["target_key"]
local skey = reverse_lookup[selected_key_value] -- Get the key name from the value
local scale = ""

-- Handle "Set to current project key"
if selected_key_value == 35 then
  if file_content:match("No key set") then
    print("No key is set in the file. Exiting the script.")
    return -- Exit the script
  end
  skey = file_content:match("^%a#?b?m?") -- Extract the key
end

-- Determine scale (major or minor)
if skey:find("m") then
  scale = "minor"
else
  scale = "major"
end

scale = scale:sub(1, 1):upper() .. scale:sub(2)

-- Print the result
print("Key: " .. skey .. " Scale: " .. scale)

if skey:sub(-1) == "m" then
  skey = skey:sub(1, -2) -- Extract everything except the last character
end

-- Print the result
print("Key without 'm': " .. skey)
-- Define the key to search for
 desired_key = skey -- Change this to the desired key (e.g., "A", "Ab", "A#")

-- Define the directory containing the chord progressions
 directory = "/opt/LogicalArdour/Drum loops, chords, and chord progressions/MIDI Progressions/"..scale.."/"

-- Function to get files in a directory
function get_files_in_directory(dir)
    local files = {}
    for file in io.popen('ls "' .. dir .. '"'):lines() do
        if file:match("%.mid$") then -- Check if the file ends with .mid
            table.insert(files, file)
        end
    end
    return files
end

-- Function to filter files by key
function filter_files_by_key(files, fkey)
    local filtered_files = {}
    for _, file in ipairs(files) do
        -- Match files that start with the exact key followed by a non-word character or `.mid`
        if file:match("^" .. fkey .. "[%W_]") or file:match("^" .. fkey .. "%.mid$") then
            table.insert(filtered_files, file)
        end
    end
    return filtered_files
end

-- Function to pick a random file
function pick_random_file(files)
    if #files == 0 then
        return nil -- No files matched
    end
    math.randomseed(os.time()) -- Seed the random number generator
    local random_index = math.random(1, #files)
    return files[random_index]
end

-- Main logic
local all_files = get_files_in_directory(directory)

local matching_files = filter_files_by_key(all_files, desired_key)

local random_file = pick_random_file(matching_files)

if random_file then
    print("Random progression in key " .. desired_key .. ": " .. random_file)
    local full_file_path = directory .. random_file
	import_midi_into_track(full_file_path, track_name)
else
    print("No progressions found for key: " .. desired_key)
 scale = scale:sub(1, 1):lower() .. scale:sub(2)

    local filepath = "/tmp/chord"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/newchord " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

import_midi_into_track(filepath, track_name)

			local delete_file = "rm -rf "..filepath

os.execute(delete_file)
end end
		if rv and rv["dropdown"] == "surgechord" then
		print("Surge XT")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Surge XT.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Chord Generation - Surge XT"

		add_track_from_template(template_path, track_name)

local sespath = Session:path()
local key_file_path = sespath .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

local scurrent_key_option = "Set to current project key: " .. file_content
local sdialog_options = {
  {
    type = "dropdown",
    key = "target_key",
    title = "Choose the key you want the session player to follow",
    values = {
      ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
      ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
      ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
      ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
      ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
      ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
      [scurrent_key_option] = 35,
      ["Do not change key"] = 36
    },
    default = scurrent_key_option
  }
}

local reverse_lookup = {}
for skey, value in pairs(sdialog_options[1].values) do
  reverse_lookup[value] = skey
end

-- Create and run the dialog
local sod = LuaDialog.Dialog("Choose Target Key", sdialog_options)
local srv = sod:run()

-- Exit if dialog is canceled
if not srv then
  print("Dialog was canceled.")
  return
end

local selected_key_value = srv["target_key"]
local skey = reverse_lookup[selected_key_value] -- Get the key name from the value
local scale = ""

-- Handle "Set to current project key"
if selected_key_value == 35 then
  if file_content:match("No key set") then
    print("No key is set in the file. Exiting the script.")
    return -- Exit the script
  end
  skey = file_content:match("^%a#?b?m?") -- Extract the key
end

-- Determine scale (major or minor)
if skey:find("m") then
  scale = "minor"
else
  scale = "major"
end

scale = scale:sub(1, 1):upper() .. scale:sub(2)

-- Print the result
print("Key: " .. skey .. " Scale: " .. scale)

if skey:sub(-1) == "m" then
  skey = skey:sub(1, -2) -- Extract everything except the last character
end

-- Print the result
print("Key without 'm': " .. skey)
-- Define the key to search for
 desired_key = skey -- Change this to the desired key (e.g., "A", "Ab", "A#")

-- Define the directory containing the chord progressions
 directory = "/opt/LogicalArdour/Drum loops, chords, and chord progressions/MIDI Progressions/"..scale.."/"

-- Function to get files in a directory
function get_files_in_directory(dir)
    local files = {}
    for file in io.popen('ls "' .. dir .. '"'):lines() do
        if file:match("%.mid$") then -- Check if the file ends with .mid
            table.insert(files, file)
        end
    end
    return files
end

-- Function to filter files by key
function filter_files_by_key(files, fkey)
    local filtered_files = {}
    for _, file in ipairs(files) do
        -- Match files that start with the exact key followed by a non-word character or `.mid`
        if file:match("^" .. fkey .. "[%W_]") or file:match("^" .. fkey .. "%.mid$") then
            table.insert(filtered_files, file)
        end
    end
    return filtered_files
end

-- Function to pick a random file
function pick_random_file(files)
    if #files == 0 then
        return nil -- No files matched
    end
    math.randomseed(os.time()) -- Seed the random number generator
    local random_index = math.random(1, #files)
    return files[random_index]
end

-- Main logic
local all_files = get_files_in_directory(directory)

local matching_files = filter_files_by_key(all_files, desired_key)

local random_file = pick_random_file(matching_files)

if random_file then
    print("Random progression in key " .. desired_key .. ": " .. random_file)
    local full_file_path = directory .. random_file
	import_midi_into_track(full_file_path, track_name)
else
    print("No progressions found for key: " .. desired_key)
 scale = scale:sub(1, 1):lower() .. scale:sub(2)

    local filepath = "/tmp/chord"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/newchord " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

import_midi_into_track(filepath, track_name)

			local delete_file = "rm -rf "..filepath

os.execute(delete_file)
end end


end end



