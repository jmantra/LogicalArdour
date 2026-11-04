ardour {
 ["type"]    = "EditorHook",
 name        = "auto save snapshot",
 author      = "Ardour Team",
 description = "Save a session-snapshot periodically (every minute) named after the current date-time in a subfolder",
}


-- subscribe to signals
function signals ()
  return LuaSignal.Set():add ({[LuaSignal.LuaTimerS] = true})
end

-- create callback function
function factory ()
  local _last_snapshot_time = 0 -- persistent variable
  local _snapshot_interval = 60 * 1 -- interval in seconds (currently set to 60 sec)



  return function (signal, ref, ...)
    local now = os.time() -- unix-time, seconds since 1970

    -- skip initial save when script is loaded
    if (_last_snapshot_time == 0) then
      _last_snapshot_time = now
    end

    if (now > _last_snapshot_time + _snapshot_interval) then
      -- don't save while recording, may interfere with recording
      if Session:actively_recording() then
        -- queue 30 sec after rec-stop
        _last_snapshot_time = now - _snapshot_interval + 30
        return
      end

       spath = Session:path()
-- Define the backup subfolder name (relative to the session folder)
local backup_folder = spath.."/backups"

-- Create the backup folder if it doesn't exist (Linux/macOS version; adjust for Windows if needed)
os.execute("mkdir -p " .. backup_folder)

      _last_snapshot_time = now
      -- format date-time (avoid colon)
      local snapshot_name = os.date ("%Y-%m-%d %H.%M.%S", now)
      -- save session snapshot to the backup subfolder
      Session:save_state(backup_folder .. "/backup " .. snapshot_name, false, false, false)
    end

  end
end
