ardour {
    ["type"] = "EditorAction",
    name = "Load Drum Soundfont",
    license = "MIT",
    author = "Justin Ehrlichman",
    description = "Open the drum soundfont browser. AVL kits replace the track plugin with that AVL drumkit. Any other kit replaces the track plugin with ACE Fluid Synth and loads the soundfont."
}

function factory () return function ()
    local fluidsynth_id = "urn:ardour:a-fluidsynth"
    local sf2_property = "urn:ardour:a-fluidsynth:sf2file"
    local browser = "/opt/LogicalArdour/drum-soundfont-browser"

    local function show_error (message)
        LuaDialog.Message("Load Drum Soundfont", message, LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
    end

    local handle = io.popen (browser)
    if not handle then
        show_error ("Could not start the drum soundfont browser:\n" .. browser)
        return
    end
    local contents = handle:read ("*a")
    handle:close ()
    if not contents or contents == "" then
        return
    end

    local soundfont_path, track_name, kind, plugin_name = contents:match ("^([^\r\n]*)\r?\n([^\r\n]*)\r?\n([^\r\n]*)\r?\n([^\r\n]*)")
    soundfont_path = (soundfont_path or ""):gsub ("%s+$", "")
    track_name = (track_name or ""):gsub ("[\r\n]+$", "")
    kind = (kind or ""):gsub ("%s+$", "")
    plugin_name = (plugin_name or ""):gsub ("[\r\n]+$", "")

    if soundfont_path == "" then
        show_error ("The browser did not return a soundfont path.")
        return
    end
    if not ARDOUR.LuaAPI.file_test (soundfont_path, ARDOUR.LuaAPI.FileTest.Exists) then
        show_error ("Soundfont not found:\n" .. soundfont_path)
        return
    end
    if track_name == "" then
        local file_name = soundfont_path:match ("([^/]+)$") or soundfont_path
        track_name = file_name:gsub ("%.sf2$", ""):gsub ("%.sf3$", "")
    end

    local sel = Editor:get_selection ()
    if sel:empty () or sel.tracks:routelist ():empty () then
        show_error ("No track selected. Please select one track.")
        return
    end
    if sel.tracks:routelist ():size () > 1 then
        show_error ("More than one track selected. Please select only one track.")
        return
    end

    local route = sel.tracks:routelist ():front ()
    local old = route:nth_plugin (0)
    if old:isnil () then
        show_error ("The selected track has no plugin to replace.")
        return
    end

    local load_soundfont = kind ~= "avl"
    local create_name = "ACE Fluid Synth"
    if not load_soundfont then
        if plugin_name == "" then
            show_error ("The browser did not name an AVL drumkit.")
            return
        end
        create_name = plugin_name
    end

    local new_plugin = ARDOUR.LuaAPI.new_plugin (Session, create_name, ARDOUR.PluginType.LV2, "")
    if not new_plugin or new_plugin:isnil () then
        show_error ("Could not create " .. create_name .. ".")
        return
    end

    route:replace_processor (old, new_plugin, nil)

    local replaced = route:nth_plugin (0)
    if replaced:isnil () then
        show_error (create_name .. " was replaced, but the new plugin could not be found.")
        return
    end

    if load_soundfont then
        local insert = replaced:to_insert ()
        if insert:isnil () or insert:plugin (0):unique_id () ~= fluidsynth_id then
            show_error ("The replacement plugin is not ACE Fluid Synth.")
            return
        end
        local ok = ARDOUR.LuaAPI.set_plugin_insert_property (insert, sf2_property, soundfont_path)
        if not ok then
            show_error ("Could not set the ACE Fluid Synth soundfont.")
            return
        end
    end

    route:set_name (track_name, nil)
end end
