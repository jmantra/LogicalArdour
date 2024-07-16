ardour {
	["type"]    = "EditorHook",
	name        = "Load guided menu",
	author      = "Justin Ehrlichman",
	description = "Present a menu on new session to load up different track templates",
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
					["Red Zepplin"] = "rz", ["Black Pearl"] = "bp", ["Mt PowerDrumkit (Accoustic Kit with Grooves)"] = "mt", ["Blonde Bop"] = "bo", ["Beat DRMR (Electronic Drum Sampler with LOTS of kits)"] = "bd",["Standard Drums (sfizz)"] = "std", ["Standard 2 Drums (sfizz)"] = "st2",["Electronic Drums"] = "eld", ["Room Drums (sfizz)"] = "rmd",   ["Power Drums (sfizz)"] = "pwd", ["Dance Drums (sfizz)"] = "dad",["Jazz Drums (sfizz)"] = "jzd"
				},["Instrument"] =

				{
					["ACE Fluid (Traditional Instruments)"] = "ac", ["Zynaddsubfx (Traditional Synth)"] = "za", ["Surge XT (Synth with a LOT of presets)"] = "st" },
						["Session Player"] = {
					["ACE Fluid (Traditional Instruments)"] = "acs", ["Zynaddsubfx (Traditional Synth)"] = "zas",["Surge XT (Synth with a LOT of presets)"] = "sts"

				},
				["Record Audio"] =

				{
					["Vocals"] = { ["Classic"] = "clv",["Bright"] = "brv", ["Compressed"] = "cov", ["Telephone"] = "tlv", ["Dance"] = "dav", ["Natural"] = "nav", ["Edge"] =  "edv",["Fuzz"] = "fzv"},
					["Guitar or Bass"] = {
					["Guitarix"] = "gx", ["Neural Amp Modeler"] = "nm"
				},
				}


			},
			default = "Choose a track type"
		}
	}

	-- Fetch the user config directory
local user_config_directory = ARDOUR.user_config_directory(8) -- get the config directory (using version 8)

-- Print the user config directory
print(user_config_directory)





-- Define the subdirectory you want to concatenate
local subdir = "route_templates"

-- Concatenate the config directory with the subdirectory
local full_path = user_config_directory .. "/" .. subdir

-- Print the full path


print (full_path)


	local od = LuaDialog.Dialog ("Choose Track", dialog_options)
	local rv = od:run()

	if rv and rv["dropdown"] == "rz" then
		print("You chose Red Zepplin")
		-- Replace the path below with the path to your track template
		-- local template_path = "/home/jman/templates/red zepplin.template"
		local template_path = full_path .. "/red zepplin.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Red Zepplin"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


	if rv and rv["dropdown"] == "bp" then
		print("You picked Black Pearl")
		-- Replace the path below with the path to your track template


		local template_path = full_path .. "/Black Pearl Drumkit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Black Pearl Drum Kit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


	if rv and rv["dropdown"] == "mt" then
		print("Mt PowerDrumkit")
		-- Replace the path below with the path to your track template
		-- local template_path = "/home/jman/templates/MT-PowerDrumKit.template"
		local template_path = full_path .. "/MT-PowerDrumKit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Mt PowerDrumkit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


	if rv and rv["dropdown"] == "bo" then
		print("blond bop")
		-- Replace the path below with the path to your track template
		--local template_path = "/home/jman/templates/Blonde Bop Drumkit.template"

		local template_path = full_path .. "/Blonde Bop Drumkit.template"


		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Blonde Bop Drumkit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

	if rv and rv["dropdown"] == "bd" then
		print("BeatDRMR")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/BeatDRMR.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Beat DRMR"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
		if rv and rv["dropdown"] == "ac" then
		print("Ace Fluid Synth")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Fluid.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ace Fluid Synth"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "za" then
		print("Zynaddsubfx")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/zfx.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Zynaddsubfx"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "st" then
		print("Surge XT")
		-- Replace the path below with the path to your track template
		-- local template_path = "/home/jman/templates/Surge XT.template"
		 local template_path = full_path .. "/Surge XT.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Surge XT"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

				if rv and rv["dropdown"] == "nm" then
		print("NAM")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/nam.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Neural Amp Modeler"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

					if rv and rv["dropdown"] == "gx" then
		print("Gutiarix")


		-- Replace the path below with the path to your track template
		  local template_path = full_path .. "/Guitarix.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Guitarix"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

						if rv and rv["dropdown"] == "clv" then
		print("Classic Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/classic.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "classic"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

						if rv and rv["dropdown"] == "brv" then
		print("Bright Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/bright.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "bright"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

						if rv and rv["dropdown"] == "cov" then
		print("Compressed Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/compressed.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "compressed"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


						if rv and rv["dropdown"] == "tlv" then
		print("telephone Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/telephone.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "telephone"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


						if rv and rv["dropdown"] == "dav" then
		print("Dance Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/dance.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "dance"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

							if rv and rv["dropdown"] == "nav" then
		print("Natural Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/natural.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "natural"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

		if rv and rv["dropdown"] == "std" then
		print("Standard Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Standard Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Standard Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

	if rv and rv["dropdown"] == "st2" then
		print("Standard 2 Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Standard 2 Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Standard 2 Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

		if rv and rv["dropdown"] == "eld" then
		print("Electronic Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Electronic Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Electronic Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


		if rv and rv["dropdown"] == "rmd" then
		print("Room Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Room Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Room Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "pwd" then
		print("Power Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Power Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Power Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "dad" then
		print("Dance Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Dance Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Dance Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "jzd" then
		print("Dance Drums")
		-- Replace the path below with the path to your track template

		local template_path = full_path .. "/Jazz Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Jazz Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "acs" then
		print("Ace Fluid Synth")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/GM Session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ace Fluid Synth Session"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

				if rv and rv["dropdown"] == "zas" then
		print("Zynaddsubfx")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/zafx session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Zynaddsubfx Session"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
		if rv and rv["dropdown"] == "sts" then
		print("Surge XT")
		-- Replace the path below with the path to your track template
		-- local template_path = "/home/jman/templates/Surge XT.template"
		 local template_path = full_path .. "/Surge XT Session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Surge XT Session"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


						if rv and rv["dropdown"] == "edv" then
		print("Edge Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Edge Vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Edge Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

							if rv and rv["dropdown"] == "fzv" then
		print("Fuzz Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Fuzz Vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Fuzz Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
else
    print("The folder was not created less than a minute ago.")
end







end end
