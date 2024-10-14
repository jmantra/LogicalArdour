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

     -- get Editor selection
    local sel = Editor:get_selection ()

    -- Instantiate the QM BarBeat Tracker
    local vamp = ARDOUR.LuaAPI.Vamp("libardourvampplugins:qm-barbeattracker", Session:nominal_sample_rate())

    -- prepare tables to hold results
    local beats = {}
    local bars = {}

    -- for each selected region
    for r in sel.regions:regionlist ():iter () do
        local ar = r:to_audioregion ()
        if ar:isnil () then
            goto next
        end

        beats[r:name ()] = {}
        bars[r:name ()] = {}

        -- callback to handle Vamp-Plugin analysis results
        function callback (feats)
            local fl = feats:table()[0]
            if fl then
                for f in fl:iter () do
                    if f.hasTimestamp then
                        local fn = Vamp.RealTime.realTime2Frame(f.timestamp, 48000)
                        table.insert(beats[r:name ()], {pos = fn, beat = tonumber(f.label)})
                    end
                end
            end

            local fl = feats:table()[1]
            if fl then
                for f in fl:iter () do
                    if f.hasTimestamp then
                        local fn = Vamp.RealTime.realTime2Frame(f.timestamp, 48000)
                        table.insert(bars[r:name ()], fn)
                    end
                end
            end
            return false -- continue, don't cancel
        end

        vamp:plugin():setParameter("Beats Per Bar", 4)

        vamp:analyze(ar:to_readable(), 0, callback)
        callback(vamp:plugin():getRemainingFeatures())
        vamp:reset()
        ::next::
    end

    -- Calculate distances between beats, ignoring the first Beat 4, and then average
    local first_beat_4_skipped = false
    local total_distance = 0
    local distance_count = 0

    for n, o in pairs(beats) do
        print("Distance between beats for region:", n)

        -- Iterate over the beats
        for i = 2, #o do
            local current_beat = o[i]['beat']
            local previous_beat = o[i-1]['beat']

            -- Skip the first occurrence of Beat 4
            if current_beat == 4 and not first_beat_4_skipped then
                first_beat_4_skipped = true
            else
                local distance = o[i]['pos'] - o[i-1]['pos']
                total_distance = total_distance + distance
                distance_count = distance_count + 1
                print("Distance between Beat " .. previous_beat .. " and Beat " .. current_beat .. ":", distance, "samples")
            end
        end
    end

    -- Calculate and print the average distance
    if distance_count > 0 then
        local average_distance = total_distance / distance_count
        print("Average distance between beats (excluding the first Beat 4):", average_distance, "samples")
    num = 48000/average_distance * 60
  print (num)

     local md = LuaDialog.Message("Estimate Tempo", num, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
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
    else
        print("No distances calculated.")

        -- local command = "bpmbin " .. quotedfilepath

        local command = "sox  " ..quotedfilepath.. " -t raw -r 48000  -e float -c 1 - | bpm"

os.execute(command)


-- Open the file in write mode



   local handle = io.popen(command)
    local firstresult = handle:read("*a")
    handle:close()

    print(firstresult)


     local md = LuaDialog.Message("Estimate Tempo", firstresult, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
    print(md:run())
    md = nil
    collectgarbage()
-- Convert the content to a number and store it in a variable
    local num = tonumber(firstresult)


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







end





end end

















