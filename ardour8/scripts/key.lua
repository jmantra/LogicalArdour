ardour {
	["type"] = "EditorAction",
	name = "Key - Get the key and scale of an audio loop",
	author      = "Justin Ehrlichman",
description = [[
Estimates the key of an audio loop for the purpose of setting a default key and scale for the Session Player, Chord Generator, and Bassline genearator to follow. This also serves as a point of reference for setting up autotune. The key and scale are stored in a text file called key.txt located in ~/.config/ardour8/key.txt
]]
}

function factory () return function (signal, ...)

-- Get the user config directory
 spath = Session:path()

-- Construct the full path to the key.txt file
 key_file_path = spath .. "/key.txt"

-- Read the contents of the key.txt file
 file = io.open(key_file_path, "r") -- Open the file in read mode
 file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end




local sel = Editor:get_selection()
local count = 0
local midi_region

for r in sel.regions:regionlist():iter() do
    count = count + 1
    if r:to_audioregion():isnil() then
        local md = LuaDialog.Message("Get Key", "The selected region is not an audio region. Current project key is set to "..file_content, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
        print(md:run())
        md = nil
        collectgarbage()
        return
    else
        audio_region = r
    end
end

if count ~= 1 then
    local md = LuaDialog.Message("Get Key", "Please select exactly 1 audio region. Current project key is set to "..file_content, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
    print(md:run())
    md = nil
    collectgarbage()
    return
end

local rn = audio_region:name()
local source = audio_region:source(0):to_filesource():path()
print(source)
local filepath = source


local quotedfilepath = '"' .. filepath .. '"'


-- Example usage:
local filename = quotedfilepath






  local command = "/opt/LogicalArdour/key " .. quotedfilepath

os.execute(command)


-- Open the file in write mode



   local handle = io.popen(command)
    local firstresult = handle:read("*a")
    handle:close()

    print(firstresult)

    -- Extract the key and scale
local dkey, scale = string.match(firstresult, "The key of the song is ([A-G#]+) (%a+)")

-- If the scale is minor, append 'm' to the key
-- Extract the key and scale
local dkey, scale = string.match(firstresult, "The key of the song is ([A-Gb#]+) (%a+)")

-- If the scale is minor, append 'm' to the key
if scale == "minor" then
    dkey = dkey .. "m"
end

print("Key: " .. dkey)
print("Scale: " .. scale)



   --  local md = LuaDialog.Message("Estimate Key", firstresult, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
   -- print(md:run())
    --md = nil
    --collectgarbage()

    local dialog_options = {
  {
   type = "dropdown", key = "target_key", title = "Estimated key of loop: " .. dkey .. " " .. scale .. " Would you like to set this as the project key? Current project key is set to "..file_content, values =
   {
    ["Do not set project key"] = 1, ["set the key of the project"] = 2
   },
   default = "Do not set project key"

   }
 }



 local od = LuaDialog.Dialog ("Estimate Key", dialog_options)
 local rv = od:run()



if rv and rv["target_key"] == 2 then

print ("setting key of project")

-- Get the user config directory
 spath = Session:path()

-- Construct the full path to the key.txt file
 key_file_path = spath .. "/key.txt"

-- Open the file in write mode (this will overwrite any existing content)
local file = io.open(key_file_path, "w")

-- Check if the file was opened successfully
if file then
    -- Optionally, you can write new content to the file
    file:write(dkey .. "  " .. scale .. "\n")

    -- Close the file
    file:close()

    -- Construct the full path to the key.txt file
 key_file_path = spath .. "/key.txt"

-- Read the contents of the key.txt file
 file = io.open(key_file_path, "r") -- Open the file in read mode
 file_content = "No key set" -- Default value if the file cannot be read

 end

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file

       local md = LuaDialog.Message("Get Key", "Current project key is now set to "..file_content, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
        print(md:run())
        md = nil
        collectgarbage()
else
    print("Error: Could not open file for writing at " .. key_file_path)
end

end


















end end
















