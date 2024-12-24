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
        ["Help - How to use Drum Track"] = "drhelp",
         ["NIN Drumkit (ACE Fluid Synth)"] = "nin",
        -- Add Step Sequencing submenu here
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
      }
    },
    default = "Choose a track type"
  }
}



	-- Fetch the user config directory
local user_config_directory = ARDOUR.user_config_directory(8) -- get the config directory (using version 8)

-- Print the user config directory
print(user_config_directory)





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
    os.execute("/bin/bash /tmp/yt.sh")
end

function create_seq(stemplate_path, strack_name, template_path, track_name)
  -- Create the first route from the specified template and track name
  Session:new_route_from_template(1, ARDOUR.PresentationInfo.max_order, stemplate_path, strack_name, ARDOUR.PlaylistDisposition.NewPlaylist)

  -- Get the selection and print track names
  local sel = Editor:get_selection()
  for r in sel.tracks:routelist():iter() do
    the_name = r:name()
    print(the_name)
  end

  -- Create the second route from the specified template and track name
  Session:new_route_from_template(1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)

  -- Get the selection again and connect MIDI input ports
  sel = Editor:get_selection()
  for r in sel.tracks:routelist():iter() do
    if not r:to_track():isnil() and not r:to_track():to_midi_track():isnil() then
      local inputmidiport = r:input():midi(0)
      inputmidiport:connect(the_name .. "/midi_out 1")
    end
  end
end



print (full_path)


	local od = LuaDialog.Dialog ("Choose Track", dialog_options)
	local rv = od:run()

	if rv and rv["dropdown"] == "rz" then
		print("You picked Red Zepplin Drumkit")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/red zepplin.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Red Zepplin Drumkit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)

	end


	if rv and rv["dropdown"] == "bp" then
		print("You picked Black Pearl")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/Black Pearl Drumkit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Black Pearl Drumkit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)

	end

		if rv and rv["dropdown"] == "nin" then
		print("You picked NIN Drunkit")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/NIN Drumkit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "NIN Drumkit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
				local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)

	end





	if rv and rv["dropdown"] == "bo" then
		print("blond bop")
		-- Replace the path below with the path to your track template
		--local template_path = "/home/jman/templates/Blonde Bop Drumkit.template"

		local template_path = full_path .. "/Blonde Bop Drumkit.template"


		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Blonde Bop Drumkit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
				local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end


		if rv and rv["dropdown"] == "ac" then
		print("Ace Fluid Synth")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Fluid.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ace Fluid Synth"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "za" then
		print("Yoshimi")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Yoshimi.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Yoshimi"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "st" then
		print("Surge XT")
		-- Replace the path below with the path to your track template
		-- local template_path = "/home/jman/templates/Surge XT.template"
		 local template_path = full_path .. "/Surge XT.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Surge XT"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

				if rv and rv["dropdown"] == "ra" then
		print("NAM")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Ratatouille.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ratatouille"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

					if rv and rv["dropdown"] == "gx" then
		print("Gutiarix")


		-- Replace the path below with the path to your track template
		  local template_path = full_path .. "/Guitarix.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Guitarix"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

						if rv and rv["dropdown"] == "clv" then
		print("Classic Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/classic.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "classic"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

						if rv and rv["dropdown"] == "brv" then
		print("Bright Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/bright.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "bright"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

						if rv and rv["dropdown"] == "cov" then
		print("Compressed Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/compressed.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "compressed"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


						if rv and rv["dropdown"] == "tlv" then
		print("telephone Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/telephone.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "telephone"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


						if rv and rv["dropdown"] == "dav" then
		print("Dance Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/dance.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "dance"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

							if rv and rv["dropdown"] == "nav" then
		print("Natural Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/natural.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "natural"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

		if rv and rv["dropdown"] == "std" then
		print("Standard Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Standard Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Standard Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
				local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

	if rv and rv["dropdown"] == "st2" then
		print("Standard 2 Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Standard 2 Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Standard 2 Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

		if rv and rv["dropdown"] == "eld" then
		print("Electronic Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Electronic Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Electronic Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end


		if rv and rv["dropdown"] == "rmd" then
		print("Room Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Room Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Room Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

			if rv and rv["dropdown"] == "pwd" then
		print("Power Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Power Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Power Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

			if rv and rv["dropdown"] == "dad" then
		print("Dance Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Dance Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Dance Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

			if rv and rv["dropdown"] == "jzd" then
		print("Dance Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Jazz Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Jazz Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

			if rv and rv["dropdown"] == "acs" then
		print("Ace Fluid Synth")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/GM Session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ace Fluid Synth Session"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)

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
  --  print("Filtering files for key:", key) -- Debugging key being searched
    for _, file in ipairs(files) do
       -- print("Checking file:", file) -- Debug each file
        -- Match files that start with the exact key followed by a non-word character or `.mid`
        if file:match("^" .. fkey .. "[%W_]") or file:match("^" .. fkey .. "%.mid$") then
         --   print("Matched file:", file) -- Debug matched files
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
--print("All files found:") -- Debug all files in the directory
--for _, file in ipairs(all_files) do print(file) end

local matching_files = filter_files_by_key(all_files, desired_key)
--print("Matching files for key " .. desired_key .. ":")
--for _, file in ipairs(matching_files) do print(file) end

local random_file = pick_random_file(matching_files)

if random_file then
    print("Random progression in key " .. desired_key .. ": " .. random_file)
    local full_file_path = directory .. random_file
print(full_file_path)
	local files = C.StringVector();



	files:push_back(full_file_path)

	local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
else
    print("No progressions found for key: " .. desired_key)
 scale = scale:sub(1, 1):lower() .. scale:sub(2)

    local filepath = "/tmp/chord"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/newchord " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

local files = C.StringVector();

	files:push_back(filepath)

	local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)

			local delete_file = "rm -rf "..filepath

os.execute(delete_file)







end

end


				if rv and rv["dropdown"] == "zas" then
		print("Yoshimi")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Yosh Session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Yoshimi Session"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
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
  --  print("Filtering files for key:", key) -- Debugging key being searched
    for _, file in ipairs(files) do
       -- print("Checking file:", file) -- Debug each file
        -- Match files that start with the exact key followed by a non-word character or `.mid`
        if file:match("^" .. fkey .. "[%W_]") or file:match("^" .. fkey .. "%.mid$") then
         --   print("Matched file:", file) -- Debug matched files
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
--print("All files found:") -- Debug all files in the directory
--for _, file in ipairs(all_files) do print(file) end

local matching_files = filter_files_by_key(all_files, desired_key)
--print("Matching files for key " .. desired_key .. ":")
--for _, file in ipairs(matching_files) do print(file) end

local random_file = pick_random_file(matching_files)

if random_file then
    print("Random progression in key " .. desired_key .. ": " .. random_file)
    local full_file_path = directory .. random_file
print(full_file_path)
	local files = C.StringVector();



	files:push_back(full_file_path)

	local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
else
    print("No progressions found for key: " .. desired_key)
 scale = scale:sub(1, 1):lower() .. scale:sub(2)

    local filepath = "/tmp/chord"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/newchord " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

local files = C.StringVector();

	files:push_back(filepath)

	local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)

		local delete_file = "rm -rf "..filepath

os.execute(delete_file)







end
	end
		if rv and rv["dropdown"] == "sts" then
		print("Surge XT")
		-- Replace the path below with the path to your track template
		-- local template_path = "/home/jman/templates/Surge XT.template"
		 local template_path = full_path .. "/Surge XT Session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Surge XT Session"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
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
  --  print("Filtering files for key:", key) -- Debugging key being searched
    for _, file in ipairs(files) do
       -- print("Checking file:", file) -- Debug each file
        -- Match files that start with the exact key followed by a non-word character or `.mid`
        if file:match("^" .. fkey .. "[%W_]") or file:match("^" .. fkey .. "%.mid$") then
         --   print("Matched file:", file) -- Debug matched files
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
--print("All files found:") -- Debug all files in the directory
--for _, file in ipairs(all_files) do print(file) end

local matching_files = filter_files_by_key(all_files, desired_key)
--print("Matching files for key " .. desired_key .. ":")
--for _, file in ipairs(matching_files) do print(file) end

local random_file = pick_random_file(matching_files)

if random_file then
    print("Random progression in key " .. desired_key .. ": " .. random_file)
    local full_file_path = directory .. random_file
print(full_file_path)
	local files = C.StringVector();



	files:push_back(full_file_path)

	local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
else
    print("No progressions found for key: " .. desired_key)
 scale = scale:sub(1, 1):lower() .. scale:sub(2)

    local filepath = "/tmp/chord"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/newchord " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

local files = C.StringVector();

	files:push_back(filepath)

	local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)



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

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

							if rv and rv["dropdown"] == "fzv" then
		print("Fuzz Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Fuzz Vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Fuzz Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

							if rv and rv["dropdown"] == "808" then
		print("808 Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/808-809 Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "808/809 Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

								if rv and rv["dropdown"] == "drl" then
		print("808 Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/drumlabooh.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "drumlabooh"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

									if rv and rv["dropdown"] == "brd" then
		print("Brush Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Brush Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Brush Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

									if rv and rv["dropdown"] == "orp" then
		print("Orchestral Perc")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Orchestral Perc.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Orchestral Perc"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

										if rv and rv["dropdown"] == "son" then
		print("SoniNeko Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/soni.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "SoniNeko Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end
	if rv and rv["dropdown"] == "al" then
	print("Alesis Drumkits")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/al.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Alesis Drumkits"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

		if rv and rv["dropdown"] == "tub" then
	print("Tube Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/tube.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Tube Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "dp" then
	print("Deeper Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/deeper.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Deeper Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "rob" then
	print("Robot Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/robot vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Robot Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
		if rv and rv["dropdown"] == "audio" then
	print("Audio")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/audio.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "audio"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


			if rv and rv["dropdown"] == "rob" then
	print("Robot Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/robot vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Robot Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
		if rv and rv["dropdown"] == "samp" then
	print("Samplv1 Sampler")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/sampler.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Samplv1 Sampler"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "bus" then
	print("Buskman's Holiday Percussion")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Buskman.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Buskman's Holiday Percussion"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end
		if rv and rv["dropdown"] == "hot" then
	print("Blonde Bop HotRod Drumkit")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/hotrod.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Blonde Bop HotRod Drumkit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
			local files = C.StringVector();
files:push_back("/opt/LogicalArdour/Drum loops, chords, and chord progressions/drumjockey/Basic Beats/Basicbeat_0001.mid")
local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)
	end

		if rv and rv["dropdown"] == "drhelp" then
	print("Drum Help")

-- Example usage
open_url_in_browser("https://youtu.be/COm3ym6Y-s8")
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
  "Step Sequencer-808-809 Drums",
  full_path .. "/808-809 Drums.template",
  "808-809 Drums"
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
end end


