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
    ["Choose Drum Plugin"] = 1, ["MTPowerDrumKit"] = 2,
    ["Red Zeppelin"] = 3,
    ["Black Pearl"] = 4,
      ["Beat DRMR"] = 5,
        ["Blonde Bop"] = 6,
        ["808/809 Drums (sfizz)"] = 7,
         ["Standard Drums (sfizz)"] = 8,
          ["Standard 2 Drums (sfizz)"] = 9,
           ["Electronic Drums (sfizz)"] = 10,
                  ["Room Drums (sfizz)"] = 11,
                      ["Power Drums (sfizz)"] = 12,
                       ["Dance Drums (sfizz)"] = 13,
						["Jazz Drums (sfizz)"] = 14
   },
   default = "Choose Drum Plugin"
  }
 }

 local od = LuaDialog.Dialog ("Choose Drum Plugin", dialog_options)
 local rv = od:run()

 local plugin_name = nil

if rv and rv["dropdown"] == 2 then
		print("You Chose MT-PowerDrumKit")
		plugin_name = "MT-PowerDrumKit"
		track_name = plugin_name

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LXVST, "")
	 end





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

	  	if rv and rv["dropdown"] == 5 then
		print("You Chose Beat DRMR")

		plugin_name = "Beat DRMR"
		track_name = plugin_name

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LXVST, "")
	 end

	  	if rv and rv["dropdown"] == 6 then
		print("You Chose Blonde Bop Drumkit")

		plugin_name = "Blonde Bop Drumkit"
		track_name = plugin_name

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


	  	if rv and rv["dropdown"] == 7 then
		print("808/809")

		plugin_name = "sfizz"
		track_name = "808/809 Drums"
		preset_name = "808"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	   	if rv and rv["dropdown"] == 8 then
		print("Standard Drums")

		plugin_name = "sfizz"
		track_name = "Standard Drums"
		preset_name = "Standard Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end



	   	if rv and rv["dropdown"] == 9 then
		print("Standard 2 Drums")

		plugin_name = "sfizz"
		track_name = "Standard 2 Drums"
		preset_name = "Standard 2 Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end



	   	if rv and rv["dropdown"] == 10 then
		print("Electronic Drums")

		plugin_name = "sfizz"
		track_name = "Electronic Drums"
		preset_name = "Electronic Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


	   	if rv and rv["dropdown"] == 11 then
		print("Room Drums")

		plugin_name = "sfizz"
		track_name = "Room Drums"
		preset_name = "Room Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


	   	if rv and rv["dropdown"] == 12 then
		print("Power Drums")

		plugin_name = "sfizz"
		track_name = "Power Drums"
		preset_name = "Power Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


	   	if rv and rv["dropdown"] == 13 then
		print("Dance Drums")

		plugin_name = "sfizz"
		track_name = "Dance Drums"
		preset_name = "Dance Drums"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	 	   	if rv and rv["dropdown"] == 14 then
		print("Jazz Drums")

		plugin_name = "sfizz"
		track_name = "Jazz Drums"
		preset_name = "Jazz Drums"

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

 if plugin_name == "sfizz" then


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

