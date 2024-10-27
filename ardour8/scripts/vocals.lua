ardour {
	["type"]    = "EditorAction",
	name        = "Vocals - Change Vocal Plugins/Presets for Audio Track",
	license     = "MIT",
	author      = "Justin Ehrlichman",
	description = [[Changes plugins/presets for vocals  based on is selected from  a dialog menu ]]
}

function factory () return function ()

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
   type = "dropdown", key = "dropdown", title = "Choose Vocal Preset", values =
   {
    ["Choose Vocal Preset"] = 1, ["Classic"] = 2,["Bright"] = 3, ["Dance"] = 4, ["Compressed"] = 5, ["Telephone"] = 6,
    ["Natural"] = 7, ["Edge"] =8, ["Fuzz Vocals"] = 9, ["Tube Vocals"] = 10,["Deeper Vocals"] = 11, ["Robot Vocals"] = 12

   },
   default = "Choose Vocal Preset"
  }
 }

 local od = LuaDialog.Dialog ("Choose Vocal Preset", dialog_options)
 local rv = od:run()

 -- Usng presets to save settings for autotune when switching vocals

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do

  local trackname =  r:name()

    if not r:to_track ():isnil () then
   local proc = r:nth_plugin (0) -- for every plugin
			if proc:isnil () then break end
			local pi = proc:to_insert ()
		preset = pi:plugin(0):last_preset()
		print (preset)

		local proc = Session:route_by_name(trackname):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
--local preset = proc:preset_by_label("classic-2")


proc:save_preset("temp")

end end end

local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:active()
print (active)
    --  assert (not new:isnil())

end end end


-- Function to clear out all plugins and name the track

function apply_preset_to_tracks(preset_name)
    local sel = Editor:get_selection ()
    -- for each selected track/bus
    for r in sel.tracks:routelist ():iter () do
        local plugs = ARDOUR.ProcessorList(); -- create a PluginList
        local i = 0;
        repeat -- iterate over all plugins/processors
            local proc = r:nth_processor (i)
            if not proc:isnil () then
                -- append plugin to list
                plugs:push_back(proc)
            end
            i = i + 1
        until proc:isnil ()

        r:remove_processors (plugs, nil)
        r:set_name(preset_name, nil)
    end
end

-- Example usage:



-- Create a function to add plugins

function add_plugin_to_selected_tracks(plugin_name, plugin_type, position)
    local sel = Editor:get_selection()
    if not Editor:get_selection():empty() and not Editor:get_selection().tracks:routelist():empty() then
        -- for each selected track
        for r in sel.tracks:routelist():iter() do
            local proc = ARDOUR.LuaAPI.new_plugin(Session, plugin_name, plugin_type, "")
            assert(not proc:isnil())
            r:add_processor_by_index(proc, position, nil, true)
        end
    end
end
if rv and rv["dropdown"] == 2 then

apply_preset_to_tracks("classic")

-- Classic Vocals


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end


add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("classic")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("classic")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("classic-2")

-- Load the preset
proc:load_preset(preset)

-- Tape Delay Simulation

add_plugin_to_selected_tracks("Tape Delay Simulation", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("classic")

-- Load the preset
proc:load_preset(preset)

-- GxReverb-Stereo

add_plugin_to_selected_tracks("GxReverb-Stereo", ARDOUR.PluginType.LV2, 5) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("classic")

-- Load the preset
proc:load_preset(preset)



-- *** End of classic vocals ****
end

if rv and rv["dropdown"] == 3 then

apply_preset_to_tracks("bright")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("bright")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("bright")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("Calf Exciter", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("bright")

-- Load the preset
proc:load_preset(preset)



add_plugin_to_selected_tracks("TAP DeEsser", ARDOUR.PluginType.LADSPA, 4) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("bright")

-- Load the preset
proc:load_preset(preset)

-- GxReverb-Stereo

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 5) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("bright-2")

-- Load the preset
proc:load_preset(preset)



-- *** End of bright vocals ****
end

if rv and rv["dropdown"] == 4 then

apply_preset_to_tracks("dance")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("Calf Exciter", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)



add_plugin_to_selected_tracks("ACE Reverb", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)

-- GxReverb-Stereo

add_plugin_to_selected_tracks("GxChorus-Stereo", ARDOUR.PluginType.LV2, 5) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 6) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(6):to_insert():plugin(6)

-- Get the preset
local preset = proc:preset_by_label("dance-2")

-- Load the preset
proc:load_preset(preset)



-- *** End of dance vocals ****
end

if rv and rv["dropdown"] == 5 then

apply_preset_to_tracks("compressed")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("compressed")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("compressed")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("compressed-2")

-- Load the preset
proc:load_preset(preset)



add_plugin_to_selected_tracks("Comb Splitter", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("compressed")

-- Load the preset
proc:load_preset(preset)

-- GxReverb-Stereo

add_plugin_to_selected_tracks("GxCompressor", ARDOUR.PluginType.LV2, 5) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("compressed")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 6) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(6):to_insert():plugin(6)

-- Get the preset
local preset = proc:preset_by_label("compressed-2")

-- Load the preset
proc:load_preset(preset)



-- *** End of compressed vocals ****
end

if rv and rv["dropdown"] == 6 then

apply_preset_to_tracks("telephone")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("telephone"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("telephone"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("telephone")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("telephone"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("telephone")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("TAP Scaling Limiter", ARDOUR.PluginType.LADSPA, 3) --first EQ of the chain

local proc = Session:route_by_name("telephone"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("telephone")

-- Load the preset
proc:load_preset(preset)



add_plugin_to_selected_tracks("Ratatouille", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("telephone"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("telephone")

-- Load the preset
proc:load_preset(preset)


add_plugin_to_selected_tracks("ACE Reverb", ARDOUR.PluginType.LV2, 5) --first EQ of the chain

local proc = Session:route_by_name("telephone"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("telephone")

-- Load the preset
proc:load_preset(preset)








-- *** End of telephone vocals ****
end

if rv and rv["dropdown"] == 7 then

apply_preset_to_tracks("natural")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("natural"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("natural"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("natural")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("natural"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("natural")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("natural"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("natural-2")

-- Load the preset
proc:load_preset(preset)


-- *** End of natural vocals ****
end

if rv and rv["dropdown"] == 8 then

apply_preset_to_tracks("edge")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("edge"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("edge"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("edge")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("edge"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("edge")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("Calf Exciter", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("edge"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("edge")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("edge"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("edge-2")

-- Load the preset
proc:load_preset(preset)


-- *** End of natural vocals ****
end

if rv and rv["dropdown"] == 9 then

apply_preset_to_tracks("fuzz")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("fuzz"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("fuzz"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("fuzz")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("fuzz"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("fuzz")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("MDA Overdrive", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("fuzz"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("fuzz")

proc:load_preset(preset)




-- *** End of natural vocals ****
end

if rv and rv["dropdown"] == 10 then

apply_preset_to_tracks("tube")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("tube"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("tube"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("tube")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("tube"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("tube")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("tube"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("tube 2")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ZamTube", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("tube"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("tube")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE Reverb", ARDOUR.PluginType.LV2, 5) --first EQ of the chain

local proc = Session:route_by_name("tube"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("tube")

-- Load the preset
proc:load_preset(preset)


-- *** End of natural vocals ****
end
 if rv and rv["dropdown"] == 11 then

apply_preset_to_tracks("deeper")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("deeper"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("deeper"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("deeper")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("deeper"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("deeper")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("Rubber Band Mono Pitch Shifter", ARDOUR.PluginType.LADSPA, 3) --first EQ of the chain

local proc = Session:route_by_name("deeper"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("deeper")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("TAP Chorus/Flanger", ARDOUR.PluginType.LADSPA, 4) --first EQ of the chain

local proc = Session:route_by_name("deeper"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("deeper")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 5) --first EQ of the chain

local proc = Session:route_by_name("deeper"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("deeper 2")

-- Load the preset
proc:load_preset(preset)




-- *** End of natural vocals ****
end

if rv and rv["dropdown"] == 12 then

apply_preset_to_tracks("robot")


add_plugin_to_selected_tracks("x42-Autotune (scales)", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("robot"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("temp")

-- Load the preset
proc:load_preset(preset)

 proc:remove_preset("temp")

 if active == false then

 local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
    old = r:nth_plugin(0)
      active =  old:deactivate()
print (active)
    --  assert (not new:isnil())

end end end end

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("robot"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("robot")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("robot"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("robot")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("LFO Phaser", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("robot"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("robot")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("MDA RingMod", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("robot"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("robot")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("TAP Chorus/Flanger", ARDOUR.PluginType.LADSPA, 5) --first EQ of the chain

local proc = Session:route_by_name("robot"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("robot")

-- Load the preset
proc:load_preset(preset)

end











end end
