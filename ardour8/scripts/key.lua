ardour {
 ["type"] = "EditorAction",
 name = "Key - Get the key of an audio loop",
 author = "Justin Ehrlichman",
 description = [[
Estimates the key of an audio loop for the purpose of autotune and setting the key for the project so other audio loops can follow if requested by the user
]]
}

function factory () return function (signal, ...)

       -- Get the user config directory
local user_config_directory = ARDOUR.user_config_directory(8)

-- Construct the full path to the key.txt file
local key_file_path = user_config_directory .. "/key.txt"

-- Read the contents of the key.txt file
local file = io.open(key_file_path, "r") -- Open the file in read mode
local file_content = "No key set" -- Default value if the file cannot be read

if file then
    file_content = file:read("*a") -- Read the entire content of the file
    file:close() -- Close the file
else
    print("Warning: Could not open file for reading at " .. key_file_path)
end

-- Prepare the dialog option with the file content
local current_key_option = "Set to current project key: " .. file_content
        local sel = Editor:get_selection()
        local count = 0
        local audio_region

        for r in sel.regions:regionlist():iter() do
            count = count + 1
            if r:to_audioregion():isnil() then
                local md = LuaDialog.Message("Get Key", "The selected region is not an audio region. The  project key is currently set to "..file_content, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
                print(md:run())
                md = nil
                collectgarbage()
                return
            else
                audio_region = r
            end
        end

        if count ~= 1 then
            local md = LuaDialog.Message("Get Key", "Please select exactly 1 audio region. The project key is currently set to "..file_content, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
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

    -- Pattern to capture the key after "key_"
    local fkey = rn:match("key_([A-G][#b]?m?)")

    if fkey then
        print("Extracted key:", fkey)

        if fkey:find("m$") then
            fkey = fkey .. " minor"
        else
            fkey = fkey .. " major"
        end
        print("Extracted key:", fkey)

        local dialog_options = {
            {
                type = "dropdown", key = "target_key", title = "Estimated key of loop: " .. fkey .. " Would you like to set this as the project key?", values = {
                    ["Do not set project key"] = 1, ["Set the key of the project"] = 2
                },
                default = "Do not set project key"
            }
        }

        local od = LuaDialog.Dialog("Estimate Key", dialog_options)
        local rv = od:run()

        if rv and rv["target_key"] == 2 then
            print("Setting key of project")

            local user_config_directory = ARDOUR.user_config_directory(8)
            local key_file_path = user_config_directory .. "/key.txt"

            local file = io.open(key_file_path, "w")
            if file then
                file:write(fkey .. "\n")
                file:close()
                print("File cleared and data written to " .. key_file_path .. " successfully.")
            else
                print("Error: Could not open file for writing at " .. key_file_path)
            end
        end
    else
        print("Key not found in filename.")
        local command = "key " .. quotedfilepath

        os.execute(command)
        local handle = io.popen(command)
        local firstresult = handle:read("*a")
        handle:close()

        print(firstresult)

        -- Extract the key and scale
        local dkey, scale = string.match(firstresult, "The key of the song is ([A-G#]+) (%a+)")
        print(dkey)

        if scale == "minor" then
            dkey = dkey .. "m"
        end

        print("Key: " .. dkey)
        print("Scale: " .. scale)

        local dialog_options = {
            {
                type = "dropdown", key = "target_key", title = "Estimated key of loop: " .. dkey .. " " .. scale .. " Would you like to set this as the project key?", values = {
                    ["Do not set project key"] = 1, ["Set the key of the project"] = 2
                },
                default = "Do not set project key"
            }
        }

        local od = LuaDialog.Dialog("Estimate Key", dialog_options)
        local rv = od:run()

        if rv and rv["target_key"] == 2 then
            print("Setting key of project")

            local user_config_directory = ARDOUR.user_config_directory(8)
            local key_file_path = user_config_directory .. "/key.txt"

            local file = io.open(key_file_path, "w")
            if file then
                file:write(dkey .. " " .. scale .. "\n")
                file:close()
                print("File cleared and data written to " .. key_file_path .. " successfully.")
            else
                print("Error: Could not open file for writing at " .. key_file_path)
            end
        end
    end
end end
