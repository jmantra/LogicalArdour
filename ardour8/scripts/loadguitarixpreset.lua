ardour {
    ["type"] = "EditorAction",
    name = "Load Guitarix Preset",
    license = "MIT",
    author = "Justin Ehrlichman",
    description = "Open the Guitarix preset browser, load the chosen preset into Guitarix on the selected audio track, and name the track after the preset."
}

function factory () return function ()
    local installed = "/opt/LogicalArdour/guitarix-preset-browser"
    local built = "/home/justin/Documents/la scripts/soundfont-browser/target/release/guitarix-preset-browser"
    local browser = installed
    if not ARDOUR.LuaAPI.file_test (browser, ARDOUR.LuaAPI.FileTest.Exists) then
        browser = built
    end

    local function show_error (message)
        LuaDialog.Message("Load Guitarix Preset", message, LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
    end

    local function shell_quote (value)
        return "'" .. value:gsub ("'", "'\\''") .. "'"
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
    if route:to_track ():isnil () or route:to_track ():to_audio_track ():isnil () then
        show_error ("No audio track selected. Please select an audio track.")
        return
    end

    local old = route:nth_plugin (0)
    if old:isnil () then
        show_error ("The selected track has no plugin to replace.")
        return
    end

    if not ARDOUR.LuaAPI.file_test (browser, ARDOUR.LuaAPI.FileTest.Exists) then
        show_error ("Could not find the Guitarix preset browser:\n" .. browser)
        return
    end

    local handle = io.popen (shell_quote (browser))
    if not handle then
        show_error ("Could not start the Guitarix preset browser:\n" .. browser)
        return
    end
    local contents = handle:read ("*a")
    handle:close ()
    if not contents or contents == "" then
        return
    end

    local label, track_name = contents:match ("^([^\r\n]*)\r?\n([^\r\n]*)")
    label = (label or ""):gsub ("%s+$", "")
    track_name = (track_name or ""):gsub ("[\r\n]+$", "")
    if label == "" then
        show_error ("The browser did not return a preset.")
        return
    end
    if track_name == "" then
        track_name = label
    end

    local new_plugin = ARDOUR.LuaAPI.new_plugin (Session, "Guitarix", ARDOUR.PluginType.VST3, "")
    if not new_plugin or new_plugin:isnil () then
        show_error ("Could not create Guitarix.")
        return
    end

    route:replace_processor (old, new_plugin, nil)

    local replaced = route:nth_plugin (0)
    if replaced:isnil () then
        show_error ("Guitarix was replaced, but the new plugin could not be found.")
        return
    end
    local insert = replaced:to_insert ()
    if insert:isnil () then
        show_error ("Guitarix was replaced, but the new plugin could not be found.")
        return
    end

    local proc = insert:plugin (0)
    local preset = proc:preset_by_label (label)
    if not preset or (preset.isnil and preset:isnil ()) then
        show_error ("Guitarix has no preset named:\n" .. label)
        return
    end
    proc:load_preset (preset)
    route:set_name (track_name, nil)
end end
