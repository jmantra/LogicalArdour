ardour {
	["type"]    = "EditorHook",
	name        = "Load guided menu",
	author      = "Justin Ehrlichman",
	description = "Present a menu on new session to load up different track templates",
}

function signals ()
	s = LuaSignal.Set()
	s:add ({
		[LuaSignal.SetSession] = true,
		[LuaSignal.LuaTimerS] = true,
	})
	return s
end

function factory ()
	-- How many consecutive seconds the engine has to be processing before
	-- the menu opens. Importing MIDI from the menu while Ardour is still
	-- starting up crashes, so wait until startup has settled.
	local SETTLE_SECONDS = 5

	local pending_path = nil
	local busy = false
	local last_samples = nil
	local ready_ticks = 0

	local function get_folder_birth_time(path)
		local command = "stat -c %W " .. string.format("%q", path)
		local handle = io.popen(command)
		if not handle then
			return nil
		end
		local result = handle:read("*a")
		handle:close()
		return tonumber(result)
	end

	local function folder_created_less_than_minute_ago(path)
		local folder_birth_time = get_folder_birth_time(path)
		-- 0 means this filesystem has no creation time
		if not folder_birth_time or folder_birth_time <= 0 then
			return false
		end
		return (os.time() - folder_birth_time) < 60
	end

	local function marker_path(path)
		return path .. "/.guided-menu-shown"
	end

	local function marker_exists(path)
		local existing = io.open(marker_path(path), "r")
		if existing then
			existing:close()
			return true
		end
		return false
	end

	local function write_marker(path)
		local created = io.open(marker_path(path), "w")
		if created then
			created:write("shown\n")
			created:close()
		end
	end

	-- Returns true when the audio engine processed samples since the last
	-- tick. Ardour versions without the binding fall back to true so the
	-- menu still opens after SETTLE_SECONDS.
	local function engine_advanced()
		local ok, samples = pcall(function()
			return Session:engine():processed_samples()
		end)
		if not ok or type(samples) ~= "number" then
			return true
		end
		local advanced = last_samples ~= nil and samples > last_samples
		last_samples = samples
		return advanced
	end

	local function reset_wait()
		last_samples = nil
		ready_ticks = 0
	end

	return function (signal, ...)
		if signal == LuaSignal.SetSession then
			if busy or not Session then
				return
			end
			local path = Session:path()
			if not path or path == "" then
				return
			end
			if marker_exists(path) or not folder_created_less_than_minute_ago(path) then
				pending_path = nil
				return
			end
			pending_path = path
			reset_wait()
			return
		end

		if signal ~= LuaSignal.LuaTimerS or not pending_path or busy then
			return
		end

		local path = pending_path
		if not Session or Session:path() ~= path or marker_exists(path) then
			pending_path = nil
			reset_wait()
			return
		end

		if not engine_advanced() then
			ready_ticks = 0
			return
		end

		ready_ticks = ready_ticks + 1
		if ready_ticks < SETTLE_SECONDS then
			return
		end

		pending_path = nil
		reset_wait()
		write_marker(path)
		busy = true
		Editor:access_action("LuaAction", "script-1")
		busy = false
	end
end
