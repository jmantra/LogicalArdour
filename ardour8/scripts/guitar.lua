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
    ["Choose Guitar Plugin"] = 1, ["Ratatouille"] = 2,
    ["Guitarix"] = 3


   },
   default = "Choose Guitar Plugin"
  }
 }

 local od = LuaDialog.Dialog ("Choose Guitar Plugin", dialog_options)
 local rv = od:run()

 local plugin_name = nil

if rv and rv["dropdown"] == 2 then
		print("You Chose Ratatouille")
		plugin_name = "Ratatouille"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
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


    end
  end
end

end end
