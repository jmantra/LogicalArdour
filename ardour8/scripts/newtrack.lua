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
    type = "dropdown", key = "dropdown", title = "Choose Track", values = {
      ["Choose a track Type"] = 1,
      ["Drum Track"] = {
        ["Red Zepplin"] = "rz", ["Black Pearl"] = "bp", ["Blonde Bop"] = "bo",
        ["Standard Drums (ACE Fluid Synth)"] = "std", ["Standard 2 Drums (ACE Fluid Synth)"] = "st2",
        ["Electronic Drums"] = "eld", ["Room Drums (ACE Fluid Synth)"] = "rmd",
        ["Power Drums (ACE Fluid Synth)"] = "pwd", ["Dance Drums (ACE Fluid Synth)"] = "dad",
        ["Jazz Drums (ACE Fluid Synth)"] = "jzd", ["808/809 Drums (ACE Fluid Synth)"] = "808",
        ["Brush Drums (ACE Fluid Synth)"] = "brd", ["Orchestral Perc (ACE Fluid Synth)"] = "orp",
        ["SoniNeko Drums (ACE Fluid Synth)"] = "son", ["Alesis Drumkits (Use C1 to change kits) (ACE Fluid Synth)"] = "al"
      },
      ["Play Software Instruments"] = {
        ["ACE Fluid (Traditional Instruments)"] = "ac", ["Yoshimi (Traditional Synth)"] = "za",
        ["Surge XT (Synth with a LOT of presets)"] = "st",["Samplv1 Sampler"] = "samp"
      },
      ["Session Player"] = {
        ["ACE Fluid (Traditional Instruments)"] = "acs", ["Yoshimi (Traditional Synth)"] = "zas",
        ["Surge XT (Synth with a LOT of presets)"] = "sts"
      },
      ["Record Audio"] = {
        ["Vocals"] = {
          ["Classic"] = "clv", ["Bright"] = "brv", ["Compressed"] = "cov",
          ["Telephone"] = "tlv", ["Dance"] = "dav", ["Natural"] = "nav",
          ["Edge"] = "edv", ["Fuzz"] = "fzv", ["Tube Vocals"] = "tub",
          ["Deeper Vocals"] = "dp", ["Robot Vocals"] = "rob"
        },
        ["Blank Audio Track"] = "audio"
      },
      ["Record Guitar or Bass"] = {
        ["Guitarix"] = "gx", ["Ratatouille"] = "ra"
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





	if rv and rv["dropdown"] == "bo" then
		print("blond bop")
		-- Replace the path below with the path to your track template
		--local template_path = "/home/jman/templates/Blonde Bop Drumkit.template"

		local template_path = full_path .. "/Blonde Bop Drumkit.template"


		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Blonde Bop Drumkit"

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
		print("Yoshimi")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Yoshimi.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Yoshimi"

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

				if rv and rv["dropdown"] == "ra" then
		print("NAM")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Ratatouille.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Ratatouille"

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
		print("Yoshimi")
		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Yosh Session.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Yoshimi Session"

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

							if rv and rv["dropdown"] == "808" then
		print("808 Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/808-drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "808/809 Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

								if rv and rv["dropdown"] == "drl" then
		print("808 Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/drumlabooh.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "drumlabooh"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

									if rv and rv["dropdown"] == "brd" then
		print("Brush Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Brush Drums.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Brush Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

									if rv and rv["dropdown"] == "orp" then
		print("Orchestral Perc")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/Orchestral Perc.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Orchestral Perc"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

										if rv and rv["dropdown"] == "son" then
		print("SoniNeko Drums")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/soni.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "SoniNeko Drums"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
	if rv and rv["dropdown"] == "al" then
	print("Alesis Drumkits")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/al.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Alesis Drumkits"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

		if rv and rv["dropdown"] == "tub" then
	print("Tube Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/tube.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Tube Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "dp" then
	print("Deeper Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/deeper.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Deeper Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end

			if rv and rv["dropdown"] == "rob" then
	print("Robot Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/robot vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Robot Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
		if rv and rv["dropdown"] == "audio" then
	print("Audio")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/audio.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "audio"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end


			if rv and rv["dropdown"] == "rob" then
	print("Robot Vocals")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/robot vocals.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Robot Vocals"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
		if rv and rv["dropdown"] == "samp" then
	print("Samplv1 Sampler")


		-- Replace the path below with the path to your track template
		local template_path = full_path .. "/sampler.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "Samplv1 Sampler"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end







end end


