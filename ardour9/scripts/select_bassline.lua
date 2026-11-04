ardour {
	["type"] = "EditorAction",
	name = "Select Bassline Track",
	author = "Justin Ehrlichman",
	description = [[
Selects the track named "Bassline" and scrolls it into view.
]]
}

function factory () return function (signal, ...)
    -- Find the route named "Bassline"
    local bassline_route = nil
    for r in Session:get_routes():iter() do
        if r:name() == "Bassline" then
            bassline_route = r
            break
        end
    end

    if bassline_route then
        -- Select the route and scroll it into view
        routeSelect(bassline_route, true, true)
    else
        print("Track 'Bassline' not found")
    end
end end

-- Selects this route.
-- NOTE: It deselects all other routes, therefore cannot be used multiple times for selecting multiple routes at once.
-- r: the route in question.
-- scrollIntoView: if true (or nil) then also scrolls the route into view.
-- unhide: if the route is hidden then this function does nothing unless this parameter is true (or nil) in which case it unhides the route.
function routeSelect(r, scrollIntoView, unhide)
    if r:is_hidden() then
        if unhide ~= nil and unhide ~= true then return end
        Editor:show_track_in_display(routeToTav(r), true)
    end

    Editor:access_action("Mixer", "select-none")

    repeat
        Editor:access_action("Editor", "select-next-route")
    until r:is_selected()

    if scrollIntoView == nil or scrollIntoView == true then
        routeScrollIntoView(r)
    end
end

-- Scrolls the mixer's route pane such that this route is visible. Typically this will make it the left-most visible
-- route but only if the available scrolling range allows it.
-- r: the route in question.
-- unhide: if the route is hidden then this function does nothing unless this parameter is true (or nil) in which case it unhides the route.
function routeScrollIntoView(r, unhide)
    if r:is_hidden() then
        if unhide ~= nil and unhide ~= true then return end
        Editor:show_track_in_display(routeToTav(r), true)
    end

    for i = 1, Session:get_stripables():size() do
        Editor:access_action("Mixer", "scroll-left")
    end

    local pos = routePosition(r)
    local numVisibleBeforeThis = 0

    for r2 in Session:get_routes():iter() do
        if routePosition(r2) < pos and not r2:is_hidden() then
            numVisibleBeforeThis = numVisibleBeforeThis + 1
        end
    end

    for i = 1, numVisibleBeforeThis do
        Editor:access_action("Mixer", "scroll-right")
    end
end

-- Returns the TimeAxisView for this route.
-- r: the route in question.
function routeToTav(r)
    return Editor:rtav_from_route(r):to_timeaxisview()
end

-- Returns strip position (presentation order), first strip = 0.
-- r: the route in question.
function routePosition(r)
    return r:presentation_info_ptr():order()
end 