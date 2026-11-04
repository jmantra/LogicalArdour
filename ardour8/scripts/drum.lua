ardour {
 ["type"] = "EditorAction",
 name = "Drummer - Change Drum Plugin on track/add and remove drum notes",
 author      = "Justin Ehrlichman",
description = [[
Replace Drum Plugin on currently selected track if a track is selected or add/removes drum notes if a midi region is selected
]]
}

function factory () return function (signal, ...)



local sel = Editor:get_selection()
local count = 0
local is_midi_region = false  -- fixed variable name

for r in sel.regions:regionlist():iter() do
    count = count + 1
    if r:to_midiregion():isnil() then
     is_midi_region = false
        --return
    else
        is_midi_region = true  -- corrected variable name
    end
end

if count > 1 then
    local md = LuaDialog.Message("Estimate Tempo", "Please select exactly 1 MIDI region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
    print(md:run())
    md = nil
    collectgarbage()
    return
end

if is_midi_region == true then  -- correct comparison
    Editor:access_action("LuaAction", "script-14")
    return  -- stop further processing
else



  -- Check if no track is selected
  if sel:empty() or sel.tracks:routelist():empty() then
    LuaDialog.Message("Error", "No track or midi drum region selected. Please select a track or midi drum region.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.OK):run()
    return
  end

  -- Check if more than one track is selected
  if sel.tracks:routelist():size() > 1 then
    LuaDialog.Message("Error", "More than one track selected. Please select only one track to continue.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.OK):run()
    return
  end


     midiTrackFound = false -- Flag to check if any MIDI track is selected

    -- for each selected track/bus
    for r in sel.tracks:routelist():iter() do
      if not r:to_track():isnil() and not r:to_track():to_midi_track():isnil() then
       midiTrackFound = true
       print("is a midi track")
      end
    end

       if  midiTrackFound == false then
      LuaDialog.Message("Error", "No MIDI track selected. Please select a MIDI track.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
      return
    end

       for r in sel.tracks:routelist():iter() do

    local proc = r:nth_plugin(0) -- for every plugin
    if proc:isnil() then break end
    local pi = proc:to_insert()
    local plugin_name = pi:plugin(0):name()
    if plugin_name == "MIDI Step Sequencer8x8" then

       LuaDialog.Message("Error", "The currently selected track is a Step Sequencer track, please select a drum track.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
      return

    end end


    for r in sel.tracks:routelist():iter() do

    local proc = r:nth_plugin(0) -- for every plugin
    if proc:isnil() then break end
    local pi = proc:to_insert()
    local plugin_name = pi:plugin(0):name()
    if plugin_name == "Arpeggiator" then

       LuaDialog.Message("Error", "The currently selected track is a Session Player track, please select a drum track.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
      return

    end

       local proc2 = r:nth_plugin(1) -- for every plugin
    if proc2:isnil() then break end
    local pi2 = proc2:to_insert()
    local plugin_name2 = pi2:plugin(1):name()
    if plugin_name2 == "MIDI Strum" then



      LuaDialog.Message("Error", "The currently selected track is a Session Player track, please select a drum track).", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
      return

end

    end

 end







local dialog_options = {
  {
   type = "dropdown", key = "dropdown", title = "Choose an action", values =
   {
    ["Change drum kit"] = 1,
    ["Connect step sequencer"] = 2
   },
   default = "Change drum kit"
  }
 }

 local od = LuaDialog.Dialog ("Drum Track", dialog_options)
 local rv = od:run()

 if not rv then
    return
 end

 step = "not set"

 if rv["dropdown"] == 2 then
		print("Step Sequencer")
			  local sel = Editor:get_selection()
  for r in sel.tracks:routelist():iter() do
    the_name = r:name()
    print(the_name)
    step = "set"
  end
  	-- Fetch the user config directory
local user_config_directory = ARDOUR.user_config_directory(8) -- get the config directory (using version 8)

print(user_config_directory)

local subdir = "route_templates"

-- Concatenate the config directory with the subdirectory
local full_path = user_config_directory .. "/" .. subdir
		 local template_path = full_path .. "/Step Sequencer.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Step Sequencer "..the_name

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
		--local nsel = Editor:get_selection()
		for r in sel.tracks:routelist():iter() do

    if not r:to_track():isnil() and not r:to_track():to_midi_track():isnil() then
      local outputmidiport = r:output():midi(0)
      outputmidiport:connect(the_name .. "/midi_in 1")
    end
  end
		return

 end

 if rv["dropdown"] ~= 1 then
    return
 end

 local function show_error (message)
    LuaDialog.Message("Drum Track", message, LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
 end

 local fluidsynth_id = "urn:ardour:a-fluidsynth"
 local sf2_property = "urn:ardour:a-fluidsynth:sf2file"
 local browser = "/opt/LogicalArdour/drum-soundfont-browser"

 local handle = io.popen (browser)
 if not handle then
    show_error ("Could not start the drum soundfont browser:\n" .. browser)
    return
 end
 local contents = handle:read ("*a")
 handle:close ()
 if not contents or contents == "" then
    return
 end

 local soundfont_path, chosen_name, kind, avl_plugin = contents:match ("^([^\r\n]*)\r?\n([^\r\n]*)\r?\n([^\r\n]*)\r?\n([^\r\n]*)")
 soundfont_path = (soundfont_path or ""):gsub ("%s+$", "")
 track_name = (chosen_name or ""):gsub ("[\r\n]+$", "")
 kind = (kind or ""):gsub ("%s+$", "")
 avl_plugin = (avl_plugin or ""):gsub ("[\r\n]+$", "")

 if soundfont_path == "" then
    show_error ("The browser did not return a soundfont path.")
    return
 end
 if not ARDOUR.LuaAPI.file_test (soundfont_path, ARDOUR.LuaAPI.FileTest.Exists) then
    show_error ("Soundfont not found:\n" .. soundfont_path)
    return
 end
 if track_name == "" then
    local file_name = soundfont_path:match ("([^/]+)$") or soundfont_path
    track_name = file_name:gsub ("%.sf2$", ""):gsub ("%.sf3$", "")
 end

 local route = Editor:get_selection ().tracks:routelist ():front ()
 local old = route:nth_plugin (0)
 if old:isnil () then
    show_error ("The selected track has no plugin to replace.")
    return
 end

 local load_soundfont = kind ~= "avl"
 local create_name = "ACE Fluid Synth"
 if not load_soundfont then
    if avl_plugin == "" then
       show_error ("The browser did not name an AVL drumkit.")
       return
    end
    create_name = avl_plugin
 end

 local new_plugin = ARDOUR.LuaAPI.new_plugin (Session, create_name, ARDOUR.PluginType.LV2, "")
 if not new_plugin or new_plugin:isnil () then
    show_error ("Could not create " .. create_name .. ".")
    return
 end

 route:replace_processor (old, new_plugin, nil)

 local replaced = route:nth_plugin (0)
 if replaced:isnil () then
    show_error (create_name .. " was replaced, but the new plugin could not be found.")
    return
 end

 if load_soundfont then
    local insert = replaced:to_insert ()
    if insert:isnil () or insert:plugin (0):unique_id () ~= fluidsynth_id then
       show_error ("The replacement plugin is not ACE Fluid Synth.")
       return
    end
    local ok = ARDOUR.LuaAPI.set_plugin_insert_property (insert, sf2_property, soundfont_path)
    if not ok then
       show_error ("Could not set the ACE Fluid Synth soundfont.")
       return
    end
 end

 route:set_name (track_name, nil)

-- Check for connected Step Sequencer and rename it
local a = Session:engine()
_, t = a:get_ports(ARDOUR.DataType("midi"), ARDOUR.PortList())

local port_name = nil
for p in t[2]:iter() do
    local name = p:name()
    local sel = Editor:get_selection()
    for r in sel.tracks:routelist():iter() do
        local current_track = r:name()
        if not r:to_track():isnil() and not r:to_track():to_midi_track():isnil() then
            local inputmidiport = r:input():midi(0)
            if inputmidiport:connected_to(name) == true then
                if name:find("/midi_out 1") then
                    correct_name = name:match("(.+)/midi_out 1")
                    print("Found connected sequencer: " .. correct_name)

                    -- Try to rename the connected sequencer
                    local track = Session:route_by_name(correct_name):to_track()
                    if not track:isnil() then
                        local i = 0
                        repeat
                            local proc = track:nth_processor(i)
                            if not proc:isnil() then
                                local proc_name = proc:display_name()
                                if proc_name == "MIDI Step Sequencer8x8" then
                                    track:set_name("Step Sequencer " .. track_name)
                                    print("Renamed sequencer to: Step Sequencer " .. track_name)
                                end
                            end
                            i = i + 1
                        until proc:isnil()
                    end
                end
            end
        end
    end
end

-- Handle special case for step=="set"
if step == "set" then
    -- ... existing step=="set" specific code ...
end
end end


