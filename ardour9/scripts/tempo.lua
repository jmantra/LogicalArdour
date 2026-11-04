ardour {
	["type"] = "EditorAction",
	name = "Tempo - Estimate  and set tempo",
	author      = "Justin Ehrlichman",
description = [[
Estimate the tempo of a selected audio region and set tempo markers or set the estimated tempo for the entire project
]]
}

function factory () return function (signal, ...)

local dialog_options = {
  {
    type = "dropdown", key = "dropdown", title = "Choose how to set tempo", values =
    {
      ["Set tempo for entire project"] = 1, ["Set tempo for length of the audio loop"] = 2
    },
    default = "Set tempo for entire project"
  }
}

local od = LuaDialog.Dialog("Choose how to set tempo", dialog_options)
local rv = od:run()

-- Exit the script if 'Cancel' is pressed or the dialog is closed
if not rv then
  return -- Exits the script
end

if rv["dropdown"] == 2 then
  dur = true
else
  dur = false
end





local sel = Editor:get_selection()
local count = 0


for r in sel.regions:regionlist():iter() do
    count = count + 1
    if r:to_audioregion():isnil() then
        local md = LuaDialog.Message("Estimate Tempo", "The selected region is not an audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
        print(md:run())
        md = nil
        collectgarbage()
        return
    else
        audio_region = r
    end
end

if count ~= 1 then
    local md = LuaDialog.Message("Estimate Tempo", "Please select exactly 1 audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
    print(md:run())
    md = nil
    collectgarbage()
    return
end

local rn = audio_region:name()
print (rn)
local source = audio_region:source(0):to_filesource():path()
--print(source)
local filepath = source

local st = audio_region:position()

print (st)

local ln = audio_region:length()
local et = st + ln
print(et)

local quotedfilepath = '"' .. filepath .. '"'

function extractBPM(rn)
    local bpm = string.match(rn, "(%d%d?%d?)[-_]?%s*[bB][pP][mM]", 1)
    if not bpm then
        bpm = string.match(rn, "[bB][pP][mM]%s*[_-]?(%d+)", 1)
    end
    return bpm
end

-- Example usage:

local bpm = extractBPM(rn)
if bpm then
    print(bpm)
    local result = bpm

    local md = LuaDialog.Message("Estimate Tempo", result, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
    print(md:run())
    md = nil
    collectgarbage()

    local num = tonumber(result)

    -- to do, add tempo markers and prompt whether or not you want to tempo markers

    -- set a tempo map
    local tm = Temporal.TempoMap.write_copy()
    if dur == true then
    tm:set_tempo(Temporal.Tempo(num, num, 4), st)
   tm:set_tempo(Temporal.Tempo(120, 120, 4), et)
   else

    tp = Temporal.timepos_t (Session:nominal_sample_rate () * 0)


     tm:set_tempo(Temporal.Tempo(num, num, 4), tp)

     end

    Session:begin_reversible_command("Change Tempo Map")
    Temporal.TempoMap.update(tm)
    if not Session:abort_empty_reversible_command() then
        Session:commit_reversible_command(nil)
    end

    tm = nil

    -- Abort Edit example
    -- after every call to Temporal.TempoMap.write_copy()
    -- there must be a matching call to
    -- Temporal.TempoMap.update() or Temporal.TempoMap.abort_update()
    Temporal.TempoMap.write_copy()
    Temporal.TempoMap.abort_update()
else
    print("BPM not found in filename.")



        -- local command = "bpmbin " .. quotedfilepath

        local command = "/opt/LogicalArdour/minibpm  " ..quotedfilepath.." > /tmp/bpm.txt"

os.execute(command)


-- Read the file
 file = io.open("/tmp/bpm.txt", "r")
 content = file:read("*all")
file:close()

-- Extract the number after "Estimated BPM:"
bpm_string = content:match("Estimated BPM:%s*([%d%.]+)")
if bpm_string == nil then
    -- Fallback: use sox | bpm if minibpm did not produce a result
    local fallback_command = "sox " .. quotedfilepath .. " -t raw -r 48000 -e float -c 1 - | bpm > /tmp/bpm.txt"
    os.execute(fallback_command)
    file = io.open("/tmp/bpm.txt", "r")
    content = file:read("*all")
    file:close()
    -- Try to extract BPM from the fallback output (assuming bpm outputs just the number or similar)
    bpm_string = content:match("([%d%.]+)")
end
bpm_number = tonumber(bpm_string)
print(bpm_number)
num = bpm_number

local md = LuaDialog.Message("Estimate Tempo", bpm_string, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
print(md:run())
md = nil
collectgarbage()


    -- set a tempo map
    local tm = Temporal.TempoMap.write_copy()
    if dur == true then
    tm:set_tempo(Temporal.Tempo(num, num, 4), st)
   tm:set_tempo(Temporal.Tempo(120, 120, 4), et)
   else

    tp = Temporal.timepos_t (Session:nominal_sample_rate () * 0)


     tm:set_tempo(Temporal.Tempo(num, num, 4), tp)

     end

    Session:begin_reversible_command("Change Tempo Map")
    Temporal.TempoMap.update(tm)
    if not Session:abort_empty_reversible_command() then
        Session:commit_reversible_command(nil)
    end

    tm = nil

    -- Abort Edit example
    -- after every call to Temporal.TempoMap.write_copy()
    -- there must be a matching call to
    -- Temporal.TempoMap.update() or Temporal.TempoMap.abort_update()
    Temporal.TempoMap.write_copy()
    Temporal.TempoMap.abort_update()



    end

    -- local command = "sox  " ..quotedfilepath.. " -t raw -r 48000  -e float -c 1 - | bpm"













end end

















