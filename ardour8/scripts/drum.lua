ardour {
 ["type"] = "EditorAction",
 name = "Drum - Change Drum Plugin",
 author      = "Justin Ehrlichman",
description = [[
Replace Drum Plugin on currently selected track
]]
}

function factory () return function (signal, ...)


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
						["Cheetah SpecDrum Electro (Drumlabooh)"] =15,
						["Cheetah SpecDrum Afro (Drumlabooh)"] =16,
						["Gretch JazzKit (Drumlabooh)"] =17,
						["Brush Drum (ACE Fluid Synth)"] = 18,
						["Orchestral Perc (ACE Fluid Synth)"] = 19

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
		track_name = "808/809 Drums"
		preset_name = "808"

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
		preset_name = "Dance Drums"

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
		print("Cheetah SpecDrum Electro")

		plugin_name = "drumlabooh"
		track_name = "Cheeatah SpecDrum Electro"
		preset_name = "cse"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.VST3, "")
	 end


	 	 	   	if rv and rv["dropdown"] == 16 then
		print("Cheetah SpecDrum Afro")

		plugin_name = "drumlabooh"
		track_name = "Cheeatah SpecDrum Afro"
		preset_name = "csa"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.VST3, "")
	 end

	 	 	   	if rv and rv["dropdown"] == 17 then
		print("Gretch JazzKit")

		plugin_name = "drumlabooh"
		track_name = "Gretch Jazzkit"
		preset_name = "gre"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.VST3, "")
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


 if plugin_name == "drumlabooh" then


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


