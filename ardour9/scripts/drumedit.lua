ardour {
   ["type"] = "EditorAction", name = "Kick/Snare Velocity",
   license     = "GPL",
   author      = "Albert Gräf",
   description = [[Modify kick and snare velocities]]
}



function factory () return function ()

-- Set this to true for debugging output in the scripting console.
local debug = true

-- Set this to true to prompt for the velocity parameters.
local interactive = true

-- Set this to the default velocities
local param = { kick_vel = 100, snare_vel = 100 }

if meter_global_param then
   param = meter_global_param
end
if interactive then
   local dialog_options = {
      { type = "slider", key = "kick_vel", title = "Kick Percentage", min = 0, max = 100, step = 1, digits = 0, default = param.kick_vel },
      { type = "button", key = "reset_kick", title = "Reset Kick Velocities" },
      { type = "slider", key = "snare_vel", title = "Snare Snare Percentage", min = 0, max = 100, step = 1, digits = 0, default = param.snare_vel },
      { type = "button", key = "reset_snare", title = "Reset Snare Velocities" },
   }
   local dg = LuaDialog.Dialog ("Kick/Snare Velocity Setup", dialog_options)
   local result = dg:run()
   if result then
      -- Handle reset buttons
      if result.reset_kick then
         param.kick_vel = 100
      end
      if result.reset_snare then
         param.snare_vel = 100
      end
      -- Update other parameters
      param.kick_vel = result.kick_vel
      param.snare_vel = result.snare_vel
      -- save the data for the next invocation
      meter_global_param = param
   else
      -- dialog canceled, exit
      return
   end
end

local sel = Editor:get_selection ()
for r in sel.regions:regionlist ():iter () do
   local mr = r:to_midiregion ()
   if mr:isnil () then goto next end

   local mm = mr:model ()
   local nl = ARDOUR.LuaAPI.note_list (mm)
   local mc = mm:new_note_diff_command ("Kick/Snare Velocity")
   for n in nl:iter () do
      local vel = n:velocity ()
      local note = n:note()
      
      -- Check if it's a kick or snare note and apply velocity reduction
      if note == 36 then -- Kick
         if param.kick_vel < 100 then
            -- For values less than 100, randomly set velocity to 0 or max
            if math.random(100) > param.kick_vel then
               vel = 0
            else
               vel = 127
            end
         else
            -- When kick_vel is 100, restore maximum velocity
            vel = 127
         end
      elseif note == 38 then -- Snare
         if param.snare_vel < 100 then
            -- For values less than 100, randomly set velocity to 0 or max
            if math.random(100) > param.snare_vel then
               vel = 0
            else
               vel = 127
            end
         else
            -- When snare_vel is 100, restore maximum velocity
            vel = 127
         end
      end
      
      -- Only modify the note if velocity changed
      if vel ~= n:velocity() then
         local n2 = ARDOUR.LuaAPI.new_noteptr(n:channel(), n:time(), n:length(), n:note(), vel)
         mc:remove(n)
         mc:add(n2)
      end
   end
   mm:apply_command(Session, mc)
   ::next::
end

end end
