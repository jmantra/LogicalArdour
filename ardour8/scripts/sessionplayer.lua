ardour {
 ["type"] = "EditorAction",
 name = "Session Player - Change Instrument Plugin for Session Player",
 author      = "Justin Ehrlichman",
description = [[
Replace Instrument Plugin on currently selected track
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

   -- for r in Session:get_routes():iter() do -- for every track/bus

    for r in sel.tracks:routelist():iter() do

    local proc = r:nth_plugin(0) -- for every plugin
    if proc:isnil() then break end
    local pi = proc:to_insert()
    local plugin_name = pi:plugin(0):name()
    if plugin_name == "Arpeggiator" then

      print("true")
      else
        print (plugin_name)
       LuaDialog.Message("Error", "The currently selected track is not a Session Player track(No Arpeggiator found or Arpeggiator in wrong order).", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
      return

    end

       local proc2 = r:nth_plugin(1) -- for every plugin
    if proc2:isnil() then break end
    local pi2 = proc2:to_insert()
    local plugin_name2 = pi2:plugin(1):name()
    if plugin_name2 == "MIDI Strum" then
      print("true")

      else
      LuaDialog.Message("Error", "The currently selected track is not a Session Player track(No MIDI Strum found or MIDI Strum not in correct order).", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
      return
    end
 end

local dialog_options = {
  {
   type = "dropdown", key = "dropdown", title = "Choose Instrument Plugin", values =
   {
    ["Choose Instrument Plugin"] = 1, ["ACE Fluid Synth"] = 2,
    ["Yoshimi"] = 3,
    ["Surge XT"] = 4,
     ["Connect Ripchord"] = 5
   },
   default = "Choose Instrument Plugin"
  }
}

local od = LuaDialog.Dialog ("Choose Instrument Plugin", dialog_options)
local rv = od:run()

if not rv then
    return
end

local plugin_name = nil
local track_name = nil
local preset_name = nil
local new = nil
local ripchord = "not set"

if rv["dropdown"] == 1 then
    LuaDialog.Message("Error", "Please select an instrument plugin.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
    return
end

if rv["dropdown"] == 2 then
    print("You Chose ACE Fluid Synth")
    plugin_name = "ACE Fluid Synth"
    preset_name = "gm"
    track_name = "ACE Fluid Synth Session"
    new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
end

if rv["dropdown"] == 3 then
    print("You Chose Yoshimi")
    plugin_name = "Yoshimi"
    track_name = "Yoshimi Session"
    new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.LV2, "")
end

if rv["dropdown"] == 4 then
    print("You Chose Surge XT")
    plugin_name = "Surge XT"
    track_name = "Surge XT Session"
    new = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, ARDOUR.PluginType.VST3, "")
end

if rv["dropdown"] == 5 then
    print("Ripchord")
    plugin_name = "Ripchord"
    local sel = Editor:get_selection()
    for r in sel.tracks:routelist():iter() do
        the_name = r:name()
        print(the_name)
        ripchord = "set"
    end
    
    local user_config_directory = ARDOUR.user_config_directory(8)
    print(user_config_directory)
    local subdir = "route_templates"
    local full_path = user_config_directory .. "/" .. subdir
    local template_path = full_path .. "/Ripchord.template"
    local track_name = "Ripchord "..the_name

    Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
    
    for r in sel.tracks:routelist():iter() do
        if not r:to_track():isnil() and not r:to_track():to_midi_track():isnil() then
            local outputmidiport = r:output():midi(0)
            outputmidiport:connect(the_name .. "/midi_in 1")
        end
    end
    return
end

if track_name == nil then
    return
end

local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty () then
    for r in sel.tracks:routelist ():iter () do
        if not r:to_track ():isnil () then
            old = r:nth_plugin(2)
            r:replace_processor (old, new, nil)
            r:set_name(track_name, nil)

            if plugin_name == "ACE Fluid Synth" and preset_name then
                local proc = Session:route_by_name(track_name):to_track():nth_plugin(2):to_insert():plugin(2)
                local preset = proc:preset_by_label(preset_name)
                proc:load_preset(preset)
            end
        end
    end
end

-- Check for ripchord
if ripchord == "not set" then
    local a = Session:engine()
    _, t = a:get_ports(ARDOUR.DataType("midi"), ARDOUR.PortList())
    
    local correct_name
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
                        print("Correct name is " .. correct_name)
                    end
                end
            end
        end
    end

    if correct_name then
        local track = Session:route_by_name(correct_name):to_track()
        if not track:isnil() then
            local i = 0
            local found_ripchord = false
            repeat
                local proc = track:nth_processor(i)
                if not proc:isnil() then
                    local proc_name = proc:display_name()
                    if proc_name == "Ripchord" then
                        found_ripchord = true
                        track:set_name("Ripchord "..track_name)
                    end
                end
                i = i + 1
            until proc:isnil()

            if not found_ripchord then
                print("Ripchord not found")
            end
        else
            print("Track '" .. correct_name .. "' not found")
        end
    end
end

end end






