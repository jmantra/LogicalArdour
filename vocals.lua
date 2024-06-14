ardour {
	["type"]    = "EditorAction",
	name        = "Vocals - Change Vocal Plugins/Presets for Audio Track",
	license     = "MIT",
	author      = "Justin Ehrlichman",
	description = [[Changes plugins/presets for vocals  based on is selected from  a dialog menu ]]
}

function factory () return function ()

-- Code block to clear all plugins on the track and change name

local sel = Editor:get_selection ()
local plugin_name = "classic"
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
		r:set_name(plugin_name, nil)
	end

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

-- GxReverb-Stereo



end end

