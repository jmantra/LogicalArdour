ardour {
	["type"]    = "EditorAction",
	name        = "Vocals - Change Vocal Plugins/Presets for Audio Track",
	license     = "MIT",
	author      = "Justin Ehrlichman",
	description = [[Changes plugins/presets for vocals  based on is selected from  a dialog menu ]]
}

function factory () return function ()

local dialog_options = {
  {
   type = "dropdown", key = "dropdown", title = "Choose Vocal Preset", values =
   {
    ["Choose Vocal Preset"] = 1, ["Classic"] = 2,["Bright"] = 3, ["Dance"] = 4, ["Compressed"] = 5

   },
   default = "Choose Vocal Preset"
  }
 }

 local od = LuaDialog.Dialog ("Choose Vocal Preset", dialog_options)
 local rv = od:run()

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

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("classic")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("classic")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("classic-2")

-- Load the preset
proc:load_preset(preset)

-- Tape Delay Simulation

add_plugin_to_selected_tracks("Tape Delay Simulation", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("classic")

-- Load the preset
proc:load_preset(preset)

-- GxReverb-Stereo

add_plugin_to_selected_tracks("GxReverb-Stereo", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("classic"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("classic")

-- Load the preset
proc:load_preset(preset)



-- *** End of classic vocals ****
end

if rv and rv["dropdown"] == 3 then

apply_preset_to_tracks("bright")

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("bright")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("bright")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("Calf Exciter", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("bright")

-- Load the preset
proc:load_preset(preset)



add_plugin_to_selected_tracks("TAP DeEsser", ARDOUR.PluginType.LADSPA, 3) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("bright")

-- Load the preset
proc:load_preset(preset)

-- GxReverb-Stereo

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("bright"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("bright-2")

-- Load the preset
proc:load_preset(preset)



-- *** End of bright vocals ****
end

if rv and rv["dropdown"] == 4 then

apply_preset_to_tracks("dance")

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("Calf Exciter", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)



add_plugin_to_selected_tracks("ACE Reverb", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)

-- GxReverb-Stereo

add_plugin_to_selected_tracks("GxChorus-Stereo", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("dance")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 5) --first EQ of the chain

local proc = Session:route_by_name("dance"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("dance-2")

-- Load the preset
proc:load_preset(preset)



-- *** End of dance vocals ****
end

if rv and rv["dropdown"] == 5 then

apply_preset_to_tracks("compressed")

-- Classic Vocals

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 0) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(0):to_insert():plugin(0)

-- Get the preset
local preset = proc:preset_by_label("compressed")

-- Load the preset
proc:load_preset(preset)

-- ACE Compressor

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 1) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(1):to_insert():plugin(1)

-- Get the preset
local preset = proc:preset_by_label("compressed")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE Compressor", ARDOUR.PluginType.LV2, 2) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(2):to_insert():plugin(2)

-- Get the preset
local preset = proc:preset_by_label("compressed-2")

-- Load the preset
proc:load_preset(preset)



add_plugin_to_selected_tracks("Comb Splitter", ARDOUR.PluginType.LV2, 3) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(3):to_insert():plugin(3)

-- Get the preset
local preset = proc:preset_by_label("compressed")

-- Load the preset
proc:load_preset(preset)

-- GxReverb-Stereo

add_plugin_to_selected_tracks("GxCompressor", ARDOUR.PluginType.LV2, 4) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(4):to_insert():plugin(4)

-- Get the preset
local preset = proc:preset_by_label("compressed")

-- Load the preset
proc:load_preset(preset)

add_plugin_to_selected_tracks("ACE EQ", ARDOUR.PluginType.LV2, 5) --first EQ of the chain

local proc = Session:route_by_name("compressed"):to_track():nth_plugin(5):to_insert():plugin(5)

-- Get the preset
local preset = proc:preset_by_label("compressed-2")

-- Load the preset
proc:load_preset(preset)



-- *** End of compressed vocals ****
end






end end
