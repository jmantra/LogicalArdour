ardour {
 ["type"] = "EditorAction",
 name = "Drum - Change Drum Plugin",
 author      = "Justin Ehrlichman",
description = [[
Replace Drum Plugin on currently selected track
]]
}

function factory () return function (signal, ...)

 local sel = Editor:get_selection ()

  -- Check if no track is selected
  if sel:empty() or sel.tracks:routelist():empty() then
    LuaDialog.Message("Error", "No track selected. Please select a track to continue.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.OK):run()
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







local dialog_options = {
  {
   type = "dropdown", key = "dropdown", title = "Choose Drum Plugin", values =
   {
    ["Choose Drum Plugin"] = 1,
    ["Red Zeppelin (AVL Drumkits)"] = 3,
    ["Black Pearl (AVL Drumkits)"] = 4,
        ["Blonde Bop(AVL Drumkits)"] = 6,
        ["808/809 Drums (ACE Fluid Synth)"] = 7,
         ["Standard Drums (ACE Fluid Synth)"] = 8,
          ["Standard 2 Drums (ACE Fluid Synth)"] = 9,
           ["Electronic Drums (ACE Fluid Synth)"] = 10,
                  ["Room Drums (ACE Fluid Synth)"] = 11,
                      ["Power Drums (ACE Fluid Synth)"] = 12,
                       ["Dance Drums (ACE Fluid Synth)"] = 13,
						["Jazz Drums (ACE Fluid Synth)"] = 14,
						["SoniNeko (ACE Fluid Synth)"] =15,
					["NIN Drumkit (ACE Fluid Synth)"] =16,
						 ["Alesis Drumkits(Use C1 to change kits) (ACE Fluid Synth)"] =17,
						["Brush Drum (ACE Fluid Synth)"] = 18,
						["Orchestral Perc (ACE Fluid Synth)"] = 19,
						["Buskman's Holiday Percussion (AVL Drumits)"] = 20,
						["Blonde Bop HotRod Drumkit (AVL Drumkits)"] = 21,
						["Connect Step Sequencer"] = 22

   },
   default = "Choose Drum Plugin"
  }
 }

 local od = LuaDialog.Dialog ("Choose Drum Plugin", dialog_options)
 local rv = od:run()

 local plugin_name = nil






 	if rv and rv["dropdown"] == 3 then
		print("You Chose Red Zeppelin Drumkit")
		plugin_name = "Red Zeppelin Drumkit"
		track_name = plugin_name

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


 	if rv and rv["dropdown"] == 4 then
		print("You Chose Black Pearl Drumkit")

		plugin_name = "Black Pearl Drumkit"
		track_name = plugin_name

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end



	  	if rv and rv["dropdown"] == 6 then
		print("You Chose Blonde Bop Drumkit")

		plugin_name = "Blonde Bop Drumkit"
		track_name = plugin_name

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


	  	if rv and rv["dropdown"] == 7 then
		print("808/809")

		plugin_name = "ACE Fluid Synth"
		track_name = "808-809 Drums"
		preset_name = "eight"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	   	if rv and rv["dropdown"] == 8 then
		print("Standard Drums")

		plugin_name = "ACE Fluid Synth"
		track_name = "Standard Drums"
		preset_name = "Standard Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end



	   	if rv and rv["dropdown"] == 9 then
		print("Standard 2 Drums")

		plugin_name = "ACE Fluid Synth"
		track_name = "Standard 2 Drums"
		preset_name = "Standard 2 Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end



	   	if rv and rv["dropdown"] == 10 then
		print("Electronic Drums")

		plugin_name = "ACE Fluid Synth"
		track_name = "Electronic Drums"
		preset_name = "Electronic Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


	   	if rv and rv["dropdown"] == 11 then
		print("Room Drums")

		plugin_name = "ACE Fluid Synth"
		track_name = "Room Drums"
		preset_name = "Room Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


	   	if rv and rv["dropdown"] == 12 then
		print("Power Drums")

		plugin_name = "ACE Fluid Synth"
		track_name = "Power Drums"
		preset_name = "Power Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


	   	if rv and rv["dropdown"] == 13 then
		print("Dance Drums")

		plugin_name = "ACE Fluid Synth"
		track_name = "Dance Drums"
		preset_name = "dance"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	 	   	if rv and rv["dropdown"] == 14 then
		print("Jazz Drums")

		plugin_name = "ACE Fluid Synth"
		track_name = "Jazz Drums"
		preset_name = "Jazz Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	  	   	if rv and rv["dropdown"] == 15 then
		print("SoniNeko")

		plugin_name = "ACE Fluid Synth"
		track_name = "SoniNeko Drums"
		preset_name = "soni"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end





	  	   	if rv and rv["dropdown"] == 16 then
		print("NIN Drumkit")

		plugin_name = "ACE Fluid Synth"
		track_name = "NIN Drumkit"
		preset_name = "nin"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	 	  	   	if rv and rv["dropdown"] == 17 then
		print("Alesis Drumkits")

		plugin_name = "ACE Fluid Synth"
		track_name = "Alesis Drumkits"
		preset_name = "al"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end






	 	 	 	   	if rv and rv["dropdown"] == 18 then
		print("Brush Drums")

		plugin_name = "ACE Fluid Synth"
		track_name = "Brush Drums"
		preset_name = "Brush Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	 	 	 	 	   	if rv and rv["dropdown"] == 19 then
		print("ACE Fluid Synth")

		plugin_name = "ACE Fluid Synth"
		track_name = "Orchestral Perc"
		preset_name = "Orchestral Perc"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	 	 	 	 	   	if rv and rv["dropdown"] == 20 then
		print("Buskman's Holiday Percussion")

		plugin_name = "Buskman's Holiday Percussion"
		track_name = "Buskman's Holiday Percussion"
		preset_name = "Buskman's Holiday Percussion"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	 	 	 	 	   	if rv and rv["dropdown"] == 21 then
		print("Blonde Bop HotRod Drumkit")

		plugin_name = "Blonde Bop HotRod Drumkit"
		track_name = "Blonde Bop HotRod Drumkit"


	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	  	 	 	   	if rv and rv["dropdown"] == 22 then
		print("Step Sequencer")
			  local sel = Editor:get_selection()
  for r in sel.tracks:routelist():iter() do
    the_name = r:name()
    print(the_name)
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









local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
 if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
    --  assert (not new:isnil())
      r:replace_processor (old, new, nil)
        r:set_name(track_name, nil)

 if plugin_name == "ACE Fluid Synth" then


local proc = Session:route_by_name(track_name):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label(preset_name)

-- Load the preset
proc:load_preset(preset)

end







    end
  end
end

end end


