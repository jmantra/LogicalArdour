	ardour {
	["type"] = "EditorAction",
	name = "Generate new bassline",
	author      = "Justin Ehrlichman",
description = [[
Remove currently selected region and generate new bassline
]]
}

-- ===== Helper Functions =====
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

function routeToTav(r)
  return Editor:rtav_from_route(r):to_timeaxisview()
end

function routePosition(r)
  return r:presentation_info_ptr():order()
end

function factory () return function (signal, ...)

-- Get the current editor selection
local selection = Editor:get_selection()
local region_list = selection.regions:regionlist()

if region_list:empty() then
  LuaDialog.Message("Remove MIDI Regions",
                    "No regions are currently selected.",
                    LuaDialog.MessageType.Warning,
                    LuaDialog.ButtonType.Ok):run()
  return
end

-- Begin an undoable operation
Session:begin_reversible_command("Remove selected MIDI region(s)")
local removed = false
local to_remove = {}
local last_route_name = nil

-- Collect all MIDI regions in the selection
for region in region_list:iter() do
  if not region:to_midiregion():isnil() then
    table.insert(to_remove, region)
  end
end

-- If no MIDI regions found, abort the operation
if #to_remove == 0 then
  LuaDialog.Message("Remove MIDI Regions",
                    "No MIDI regions among the selected items.",
                    LuaDialog.MessageType.Warning,
                    LuaDialog.ButtonType.Ok):run()
  Session:abort_reversible_command()
  return
end

-- Remove each selected MIDI region from its playlist
for _, region in ipairs(to_remove) do
  last_route_name = region:playlist():name()
  print("Removing region from:", last_route_name)
  region:playlist():remove_region(region)
  removed = true
end

-- Finalize the undo command
if removed then
  Session:commit_reversible_command(nil)
else
  Session:abort_reversible_command()
end

-- Find the route from which the last region was removed
local target_route = nil
for r in Session:get_routes():iter() do
  if r:name() == last_route_name then
    target_route = r
    break
  end
end

if target_route then
  routeSelect(target_route, true, true)
else
  print("Track '" .. (last_route_name or "nil") .. "' not found")
end

local user_config_directory = ARDOUR.user_config_directory(8)

-- Define the subdirectory you want to concatenate
local subdir = "route_templates"

-- Concatenate the config directory with the subdirectory
local full_path = user_config_directory .. "/" .. subdir





	local template_path = full_path .. "/Bassline.template"




local sespath = Session:path()
local key_file_path = sespath .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

local scurrent_key_option = "Set to current project key: " .. file_content
local sdialog_options = {
  {
    type = "dropdown",
    key = "target_key",
    title = "Choose the key you want the session player to follow",
    values = {
      ["C"] = 1, ["C#"] = 2, ["Db"] = 3, ["D"] = 4, ["D#"] = 5, ["Eb"] = 6,
      ["E"] = 7, ["F"] = 8, ["F#"] = 9, ["Gb"] = 10, ["G"] = 11, ["G#"] = 12, ["Ab"] = 13,
      ["A"] = 14, ["A#"] = 15, ["Bb"] = 16, ["B"] = 17,
      ["Am"] = 18, ["A#m"] = 19, ["Bbm"] = 20, ["Bm"] = 21, ["Cm"] = 22,
      ["C#m"] = 23, ["Dbm"] = 24, ["Dm"] = 25, ["D#m"] = 26, ["Ebm"] = 27,
      ["Em"] = 28, ["Fm"] = 29, ["F#m"] = 30, ["Gbm"] = 31, ["Gm"] = 32, ["G#m"] = 33, ["Abm"] = 34,
      [scurrent_key_option] = 35,
      ["Do not change key"] = 36
    },
    default = scurrent_key_option
  }
}

local reverse_lookup = {}
for skey, value in pairs(sdialog_options[1].values) do
  reverse_lookup[value] = skey
end

-- Create and run the dialog
local sod = LuaDialog.Dialog("Choose Target Key", sdialog_options)
local srv = sod:run()

-- Exit if dialog is canceled
if not srv then
  print("Dialog was canceled.")
  return
end

local selected_key_value = srv["target_key"]
local skey = reverse_lookup[selected_key_value] -- Get the key name from the value
local scale = ""

-- Handle "Set to current project key"
if selected_key_value == 35 then
  if file_content:match("No key set") then
    print("No key is set in the file. Exiting the script.")
    return -- Exit the script
  end
  skey = file_content:match("^%a#?b?m?") -- Extract the key
end

-- Determine scale (major or minor)
if skey:find("m") then
  scale = "minor"
else
  scale = "major"
end

--scale = scale:sub(1, 1):upper() .. scale:sub(2)

-- Print the result
print("Key: " .. skey .. " Scale: " .. scale)

if skey:sub(-1) == "m" then
  skey = skey:sub(1, -2) -- Extract everything except the last character
end

-- Print the result
print("Key without 'm': " .. skey)
-- Define the key to search for
 desired_key = skey -- Change this to the desired key (e.g., "A", "Ab", "A#")



    local filepath = "/tmp/bassline"..desired_key..scale..".mid"


local quotedfilepath = '"' .. filepath .. '"'

local command = "/opt/LogicalArdour/bassline_generator " .. desired_key.." "..scale.." 4 --output "..quotedfilepath

os.execute(command)

local files = C.StringVector();

	files:push_back(filepath)

	local pos = Temporal.timepos_t(0)
	Editor:do_import (files,
		Editing.ImportDistinctFiles, Editing.ImportToTrack, ARDOUR.SrcQuality.SrcBest,
		ARDOUR.MidiTrackNameSource.SMFFileAndTrackName, ARDOUR.MidiTempoMapDisposition.SMFTempoIgnore,
		pos, ARDOUR.PluginInfo(), ARDOUR.Track(), false)

			local delete_file = "rm -rf "..filepath

os.execute(delete_file)
end end
