ardour {
	["type"]    = "EditorHook",
	name        = "Create key file",
	author      = "Justin Ehrlichman",
	description = "Create text file to store the projects current key for autotune and transposition",
}



function signals ()
	s = LuaSignal.Set()
	s:add ({[LuaSignal.SetSession] = true})
	return s
end

function factory () return function (signal, ...)


local path  = Session:path()
print(path)

local function get_folder_birth_time(path)
    local command = "stat -c %W " .. path
    local handle = io.popen(command)
    local result = handle:read("*a")
    handle:close()
    return tonumber(result)
end


local function folder_created_less_than_minute_ago(path)
    local folder_birth_time = get_folder_birth_time(path)
    if folder_birth_time then
        local current_time = os.time()
        local difference = current_time - folder_birth_time
        return difference < 60  -- 60 seconds = 1 minute
    else
        return false  -- Unable to get the birth time
    end
end
local is_less_than_minute_ago = folder_created_less_than_minute_ago(path)

if is_less_than_minute_ago then

keycommand = "/opt/LogicalArdour/keystore.sh "..path

os.execute(keycommand)
else

print("Session not created less than a minute ago")

end



end end
