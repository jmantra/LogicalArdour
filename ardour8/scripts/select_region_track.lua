-- select_region_track.lua
-- Script to select the track associated with a selected region in Ardour

function select_region_track()
    print("Starting select_region_track function")
    
    -- Get the current session
    local session = Session()
    print("Session object:", session)
    if not session then
        print("No active session")
        return
    end

    -- Get the editor
    local editor = Editor()
    print("Editor object:", editor)
    if not editor then
        print("No editor available")
        return
    end

    -- Get the selection
    local selection = editor:get_selection()
    print("Selection object:", selection)
    if not selection then
        print("No selection available")
        return
    end

    -- Get the selected regions
    local regions = selection:regions()
    print("Number of selected regions:", regions and #regions or 0)
    if not regions or #regions == 0 then
        print("No region selected")
        return
    end

    -- Get the first selected region
    local region = regions[1]
    print("Selected region:", region)
    if not region then
        print("Could not get selected region")
        return
    end

    -- Get the track associated with the region
    local track = region:track()
    print("Associated track:", track)
    if not track then
        print("Could not get track for selected region")
        return
    end

    -- Clear current selection
    editor:clear_selection()
    print("Cleared current selection")

    -- Select the track
    editor:select_track(track)
    print("Selected track: " .. track:name())
end

-- Register the script
function script_params()
    return {
        { name = "Select Region Track", type = "trigger" }
    }
end

function script_run()
    print("Script started")
    select_region_track()
    print("Script finished")
end 