ardour {
	["type"]    = "EditorHook",
	name        = "Load guided menu",
	author      = "Justin Ehrlichman",
	description = "Present a menu to load up different track templates",
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
    print("The folder was created less than a minute ago.")
    local dialog_options = {
		{
			type = "dropdown", key = "dropdown", title = "Choose Track", values =
			{
				["Choose a track Type"] = 1, ["Drum Track"] =

				{
					["Red Zepplin"] = "rz", ["Black Pearl"] = "bp", ["Mt PowerDrumkit (Accoustic Kit with Grooves)"] = "mt", ["Blonde Bop"] = "bo", ["Beat DRMR (Electronic Drum Sampler with LOTS of kits)"] = "bd"
				},["Instrument"] =

				{
					["ACE Fluid (Traditional Instruments)"] = "ac", ["Zynaddsubfx (Traditional Synth)"] = "za", ["Surge XT (Synth with a LOT of presets)"] = "st"
				},
				["Record Audio"] =

				{
					["Voice"] = "vc", ["Guitar or Bass"] = "gt"
				}


			},
			default = "Choose a track type"
		}
	}

	local od = LuaDialog.Dialog ("Choose Track", dialog_options)
	local rv = od:run()

	if rv and rv["dropdown"] == "rz" then
		print("You chose Red Zepplin")
		-- Replace the path below with the path to your track template
		local template_path = "/home/jman/templates/red zepplin.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Red Zepplin"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


	if rv and rv["dropdown"] == "bp" then
		print("You picked Black Pearl")
		-- Replace the path below with the path to your track template
		local template_path = "/home/jman/templates/Black Pearl Drumkit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Black Pearl Drum Kit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


	if rv and rv["dropdown"] == "mt" then
		print("Mt PowerDrumkit")
		-- Replace the path below with the path to your track template
		local template_path = "/home/jman/templates/MT-PowerDrumKit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Mt PowerDrumkit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


	if rv and rv["dropdown"] == "bo" then
		print("bblond bop")
		-- Replace the path below with the path to your track template
		local template_path = "/home/jman/templates/Blonde Bop Drumkit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Blonde Bop Drumkit "

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

	if rv and rv["dropdown"] == "bd" then
		print("bblond bop")
		-- Replace the path below with the path to your track template
		local template_path = "/home/jman/templates/BeatDRMR.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Beat DRMR"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
		if rv and rv["dropdown"] == "ac" then
		print("Ace Fluid Synth")
		-- Replace the path below with the path to your track template
		local template_path = "/home/jman/templates/Fluid.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ace Fluid Synth"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "za" then
		print("Zynaddsubfx")
		-- Replace the path below with the path to your track template
		local template_path = "/home/jman/templates/zfx.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Zynaddsubfx"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "st" then
		print("Surge XT")
		-- Replace the path below with the path to your track template
		local template_path = "/home/jman/templates/Surge XT.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Surge XT"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

				if rv and rv["dropdown"] == "gt" then
		print("Guitar")
		-- Replace the path below with the path to your track template
		local template_path = "/home/jman/templates/nam.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Neural Amp Modeler"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

else
    print("The folder was not created less than a minute ago.")
end







end end

