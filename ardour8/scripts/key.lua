ardour {
	["type"] = "EditorAction",
	name = "Key - Get the key of an audio loop",
	author      = "Justin Ehrlichman",
description = [[
Estimates the key of an audio loop for the purpose of autotune and setting the key for the project so other audio loops can follow if requested by the user
]]
}

function factory () return function (signal, ...)




local sel = Editor:get_selection()
local count = 0
local midi_region

for r in sel.regions:regionlist():iter() do
    count = count + 1
    if r:to_audioregion():isnil() then
        local md = LuaDialog.Message("Get Key", "The selected region is not an audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
        print(md:run())
        md = nil
        collectgarbage()
        return
    else
        audio_region = r
    end
end

if count ~= 1 then
    local md = LuaDialog.Message("Get Key", "Please select exactly 1 audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
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






  local command = "key " .. quotedfilepath

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
   type = "dropdown", key = "target_key", title = "Estimated key of loop: " .. dkey .. " " .. scale .. " Would you like to set this as the project key?", values =
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
local user_config_directory = ARDOUR.user_config_directory(8)

-- Construct the full path to the key.txt file
local key_file_path = user_config_directory .. "/key.txt"

-- Open the file in write mode (this will overwrite any existing content)
local file = io.open(key_file_path, "w")

-- Check if the file was opened successfully
if file then
    -- Optionally, you can write new content to the file
    file:write(dkey .. "  " .. scale .. "\n")

    -- Close the file
    file:close()
    print("File cleared and data written to " .. key_file_path .. " successfully.")
else
    print("Error: Could not open file for writing at " .. key_file_path)
end

end


















end end
















