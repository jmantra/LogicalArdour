ardour {
 ["type"] = "EditorAction",
 name = "Guitar - Change Gutiar Plugin",
 author      = "Justin Ehrlichman",
description = [[
Replace Guitar Plugin on currently selected track
]]
}

function factory () return function (signal, ...)


local dialog_options = {
  {
   type = "dropdown", key = "dropdown", title = "Choose Guitar Plugin", values =
   {
    ["Choose Guitar Plugin"] = 1, ["Neural Amp Modeler"] = 2,
    ["Guitarix"] = 3


   },
   default = "Choose Guitar Plugin"
  }
 }

 local od = LuaDialog.Dialog ("Choose Guitar Plugin", dialog_options)
 local rv = od:run()

 local plugin_name = nil

if rv and rv["dropdown"] == 2 then
		print("You Chose Neural Amp Modeler")
		plugin_name = "NeuralAmpModeler"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.VST3, "")
	 end





 	if rv and rv["dropdown"] == 3 then
		print("You Chose Guitarix")
		plugin_name = "Guitarix"

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
        r:set_name(plugin_name, nil)

   local proc = Session:route_by_name(plugin_name):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("default")

-- Load the preset
proc:load_preset(preset)
    end
  end
end

end end
