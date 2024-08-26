



function factory () return function ()

-- Define a function that takes the sf2 file path as a parameter
function update_sf2_file_path(sf2_path)
    local sel = Editor:get_selection()
    -- Iterate through each selected track/bus
    for r in sel.tracks:routelist():iter() do
        local proc = r:nth_plugin(0) -- For every plugin
        if proc:isnil() then break end
        local pi = proc:to_insert()
        if pi:plugin(0):unique_id() == "urn:ardour:a-fluidsynth" then
            -- Print current sf2 file path
            print(ARDOUR.LuaAPI.get_plugin_insert_property(pi, "urn:ardour:a-fluidsynth:sf2file"))
            -- Set the new sf2 file path
            print(ARDOUR.LuaAPI.set_plugin_insert_property(pi, "urn:ardour:a-fluidsynth:sf2file", sf2_path))
            -- In case of ZeroConvo.lv2, the new value will only be returned once the IR is loaded
            print(ARDOUR.LuaAPI.get_plugin_insert_property(pi, "http://gareus.org/oss/lv2/zeroconvolv#ir"))
        end
    end
end

-- Example usage of the function
update_sf2_file_path("/home/jman/test.sf2")

end end

end end
