ardour {
	["type"] = "EditorAction",
	name = "New Track - Dialog Menu",
	author      = "Justin Ehrlichman",
description = [[
Brings up a dialog menu to select track types based on templates
]]
}

function factory () return function (signal, ...)

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
					["Vocals"] = { ["Classic"] = "clv",["Bright"] = "brv", ["Compressed"] = "cov", ["Telephone"] = "tlv", ["Dance"] = "dav", ["Natural"] = "nav"},
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




end end


