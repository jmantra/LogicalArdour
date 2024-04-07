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
        ["Blonde Bop"] = 6
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

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LXVST, "")
	 end





 	if rv and rv["dropdown"] == 3 then
		print("You Chose Red Zeppelin Drumkit")
		plugin_name = "Red Zeppelin Drumkit"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end


 	if rv and rv["dropdown"] == 4 then
		print("You Chose Black Pearl Drumkit")

		plugin_name = "Black Pearl Drumkit"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
	 end

	  	if rv and rv["dropdown"] == 5 then
		print("You Chose Beat DRMR")

		plugin_name = "Beat DRMR"

	 new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LXVST, "")
	 end

	  	if rv and rv["dropdown"] == 6 then
		print("You Chose Blonde Bop Drumkit")

		plugin_name = "Blonde Bop Drumkit"

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


function icon (params) return function (ctx, width, height)
	local x = width * .5
	local y = height * .5
	local r = math.min (x, y) * .7
	ctx:save ()
	ctx:translate (x, y)
	ctx:scale (1, .5)
	ctx:translate (-x, -y)
	ctx:arc (x, y, r, 0, 2 * math.pi)
	ctx:set_source_rgba (.9, .9, 1, 1)
	ctx:fill ()
	ctx:arc (x, y, r, 0, math.pi)
	ctx:arc_negative (x, y * 1.6, r, math.pi, 0)
	ctx:set_source_rgba (.7, .7, .7, 1)
	ctx:fill ()
	ctx:restore ()

	ctx:set_source_rgba (.6, .4, .2, 1)
	ctx:translate (x, y)
	ctx:scale (.7, 1)
	ctx:translate (-x, -y)
	ctx:set_line_cap (Cairo.LineCap.Round)

	function drumstick (xp, lr)
		ctx:set_line_width (r * .3)
		ctx:move_to (x * xp, y)
		ctx:close_path ()
		ctx:stroke ()
		ctx:set_line_width (r * .2)
		ctx:move_to (x * xp, y)
		ctx:rel_line_to (lr * x, y)
		ctx:stroke ()
	end
	drumstick (1.2, 1.2)
	drumstick (0.7, -.5)
end end



