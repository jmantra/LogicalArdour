ardour {
  ["type"] = "EditorAction",
  name = "Guitar - Change Guitar Plugin",
  author = "Justin Ehrlichman",
  description = [[
Replace Guitar Plugin on currently selected track
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
audioTrackFound = false -- Flag to check if any audio track is selected

    -- for each selected track/bus
    for r in sel.tracks:routelist():iter() do
      if not r:to_track():isnil() and not r:to_track():to_audio_track():isnil() then
       audioTrackFound = true
       print("is an audio track")
      end
    end

       if  audioTrackFound == false then
      LuaDialog.Message("Error", "No audio track selected. Please select an audio track.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
      return
    end

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

  local od = LuaDialog.Dialog("Choose Guitar Plugin", dialog_options)
  local rv = od:run()
  local plugin_name = nil
  local new = nil

  if rv and rv["dropdown"] == 2 then
    print("You Chose Ratatouille")
    plugin_name = "Ratatouille"
    new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
  elseif rv and rv["dropdown"] == 3 then
    print("You Chose Guitarix")
    plugin_name = "Guitarix"
    new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.VST3, "")
  else
    return
  end

  -- For the selected track, replace the plugin
  for r in sel.tracks:routelist():iter() do
    if not r:to_track():isnil() then
      local old = r:nth_plugin(0)
      r:replace_processor(old, new, nil)
      r:set_name(plugin_name, nil)
    end
  end

  if plugin_name == "Ratatouille" then


local proc = Session:route_by_name("Ratatouille"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset

local preset = proc:preset_by_label("new")

-- Load the preset
proc:load_preset(preset)

end

end end
