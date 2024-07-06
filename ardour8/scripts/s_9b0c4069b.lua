ardour { ["type"] = "Snippet", name = "Dialog Test" }

function factory () return function ()

	local dialog_options = {
		{
			type = "dropdown", key = "dropdown", title = "Choose Track", values =
			{
				["Option 1"] = 1, ["Option 2"] = "2", ["Callback"] = func,
				["Option 4"] =
				{
					["Option 4a"] = "test", ["Option 4b"] = 4.2
				}
			},
			default = "Option 2"
		}
	}

	local od = LuaDialog.Dialog ("Choose Track", dialog_options)
	local rv = od:run()

	if rv and rv["dropdown"] == "2" then
		print("You picked option 2")
		-- Replace the path below with the path to your track template
		local template_path = "~/.config/ardour8/route_templates/MT-PowerDrumKit.template"

		-- Replace "Track Name" with the name you want for your new track
		local track_name = "MT PowerDrumkit"

		Session:new_route_from_template (1, ARDOUR.PresentationInfo.max_order, template_path, track_name, ARDOUR.PlaylistDisposition.NewPlaylist)
	end
end end
