ardour {
 ["type"] = "EditorAction",
 name = "Session Player - Change Instrument Plugin for Session Player",
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
    ["Choose Instrument Plugin"] = 1, ["General MIDI Synth"] = 2,
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
		print("You Chose General MIDI Synth")
		plugin_name = "General MIDI Synth"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end





 	if rv and rv["dropdown"] == 3 then
		print("You Chose ZynAddSubFX")
		plugin_name = "ZynAddSubFX"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


 	if rv and rv["dropdown"] == 4 then
		print("You Chose Surge XT")

		plugin_name = "Surge XT"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.VST3, "")
	 end



local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(1)
    --  assert (not new:isnil())
      r:replace_processor (old, new, nil)
        r:set_name(plugin_name, nil)

       -- if plugin_name == "Dance" or plugin_name == "808" then
      -- local proc = Session:route_by_name(plugin_name):to_track():nth_plugin(0):to_insert():plugin(0)
      -- Get the preset
--local preset = proc:preset_by_label(plugin_name)

-- Load the preset
--proc:load_preset(preset)
       --end
    end
  end
end

end end





