ardour {
 ["type"] = "EditorAction",
 name = "Instrument - Change Instrument Plugin",
 author      = "Justin Ehrlichman",
description = [[
Replace Instrument Plugin on currently selected track
]]
}

function factory () return function (signal, ...)


local dialog_options = {
  {
   type = "dropdown", key = "dropdown", title = "Choose Instrument Plugin", values =
   {
    ["Choose Instrument Plugin"] = 1, ["ACE Fluid Synth"] = 2,
    ["Zynaddsubfx"] = 3,
    ["Surge XT"] = 4

   },
   default = "Choose Instrument Plugin"
  }
 }

 local od = LuaDialog.Dialog ("Choose Instrument Plugin", dialog_options)
 local rv = od:run()

 local plugin_name = nil

if rv and rv["dropdown"] == 2 then
		print("ACE Fluid Synth")
		plugin_name = "ACE Fluid Synth"
		track_name = plugin_name
		preset_name = "gm"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end





 	if rv and rv["dropdown"] == 3 then
		print("You Chose ZynAddSubFX")
		plugin_name = "ZynAddSubFX"
		track_name = plugin_name

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


 	if rv and rv["dropdown"] == 4 then
		print("You Chose Surge XT")

		plugin_name = "Surge XT"
		track_name = plugin_name

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.VST3, "")
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






