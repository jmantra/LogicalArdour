ardour {
	["type"]    = "EditorHook",
	name        = "Set preset to track name",
	author      = "Justin Ehrlichman",
	description = "Change track name when preset is changed",
}



function signals ()
	s = LuaSignal.Set()
	s:add ({[LuaSignal.Change] = true})
	return s
end

function factory () return function (signal, ...)

local sel = Editor:get_selection ()
if not sel:empty () and not sel.tracks:routelist ():empty ()  then
  -- for each selected track
  for r in sel.tracks:routelist ():iter () do
    if not r:to_track ():isnil () then
   local proc = r:nth_plugin (0) -- for every plugin
			if proc:isnil () then break end
			local pi = proc:to_insert ()
		if pi:plugin(0):unique_id() == "urn:ardour:a-fluidsynth" then
                        print ("Success")
				 sf2 = (ARDOUR.LuaAPI.get_plugin_insert_property(pi, "urn:ardour:a-fluidsynth:sf2file"))
                               print (sf2)
				local file_path = sf2

-- Function to extract the file name without the path and extension
local function extract_file_name(path)
    -- Find the last occurrence of '/' and extract the substring after it
    local file_name_with_extension = path:match("^.+/(.+)$")

    -- Remove the '.sf2' extension
    local file_name = file_name_with_extension:match("(.+)%..+$")

    return file_name
end

-- Get the file name without the path and extension
local file_name = extract_file_name(file_path)

-- Print the result
print(file_name)
r:set_name(file_name, nil)
		end
	end
end



    end




end end


