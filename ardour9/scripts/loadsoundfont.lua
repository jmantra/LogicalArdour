ardour {
    ["type"] = "EditorAction",
    name = "Load Soundfont",
    license = "MIT",
    author = "Justin Ehrlichman",
    description = "Open the soundfont browser, then load the chosen font into ACE Fluid Synth on the selected track."
}

function factory () return function ()
    local fluidsynth_id = "urn:ardour:a-fluidsynth"
    local sf2_property = "urn:ardour:a-fluidsynth:sf2file"
    local browser = "/opt/LogicalArdour/soundfont-browser"

    local function show_error (message)
        LuaDialog.Message("Load Soundfont", message, LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run()
    end

    local handle = io.popen (browser)
    if not handle then
        show_error ("Could not start the soundfont browser:\n" .. browser)
        return
    end
    local contents = handle:read ("*a")
    handle:close ()
    if not contents or contents == "" then
        return
    end

    local soundfont_path, track_name = contents:match ("^([^\r\n]*)\r?\n(.*)$")
    if not soundfont_path then
        soundfont_path = contents:gsub ("[\r\n]+$", "")
        track_name = ""
    end
    soundfont_path = soundfont_path:gsub ("%s+$", "")
    track_name = (track_name or ""):gsub ("[\r\n]+$", "")

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
    local old = nil
    local index = 0
    while true do
        local proc = route:nth_plugin (index)
        if proc:isnil () then
            break
        end
        local pi = proc:to_insert ()
        if not pi:isnil () and pi:plugin (0):unique_id () == fluidsynth_id then
            old = proc
            break
        end
        index = index + 1
    end

    if not old then
        show_error ("ACE Fluid Synth was not found on the selected track.")
        return
    end

    local new_plugin = ARDOUR.LuaAPI.new_plugin (Session, "ACE Fluid Synth", ARDOUR.PluginType.LV2, "")
    if not new_plugin or new_plugin:isnil () then
        show_error ("Could not create a new ACE Fluid Synth.")
        return
    end

    -- A new instance has no channel program yet. Set the soundfont before any preset load
    -- so channel 1 takes a preset from this font instead of the previous one.
    route:replace_processor (old, new_plugin, nil)

    local replaced = route:nth_plugin (index)
    if replaced:isnil () then
        show_error ("ACE Fluid Synth was replaced, but the new plugin could not be found.")
        return
    end

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

    route:set_name (track_name, nil)
end end
