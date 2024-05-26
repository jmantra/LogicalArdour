ardour {
	["type"] = "EditorAction",
	name = "Tempo - Estimate Tempo",
	author      = "Justin Ehrlichman",
description = [[
Estimate the tempo of a selected audio region and set tempo markers
]]
}

-- In order for this script to work please download bpmbin from my Google Drive at this URL (https://drive.google.com/file/d/1Lda5WIYD2WcxZpkKeXbix9QoEcx5xIhd/view?usp=sharing)
-- then copy to your /usr/bin directory 
--bpmbin is a compiled binary based on bpmbin.py found in this repo

function factory () return function (signal, ...)




local sel = Editor:get_selection()
local count = 0
local midi_region

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
local source = audio_region:source(0):to_filesource():path()
print(source)
local filepath = source

local st = audio_region:position()

local ln = audio_region:length()
local et = st + ln
print(et)

local quotedfilepath = '"' .. filepath .. '"'

function extractBPM(filename)
    local bpm = string.match(filename, "(%d%d?%d?)[-_]?%s*[bB][pP][mM]", 1)
    if not bpm then
        bpm = string.match(filename, "[bB][pP][mM]%s*[_-]?(%d+)", 1)
    end
    return bpm
end

-- Example usage:
local filename = quotedfilepath
local bpm = extractBPM(filename)
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
    tm:set_tempo(Temporal.Tempo(num, num, 4), st)
    tm:set_tempo(Temporal.Tempo(120, 120, 4), et)

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

    -- local command = "sox  " ..quotedfilepath.. " -t raw -r 48000  -e float -c 1 - | bpm"



  local command = "bpmbin " .. quotedfilepath

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
    tm:set_tempo(Temporal.Tempo(num, num, 4), st)
    tm:set_tempo(Temporal.Tempo(120, 120, 4), et)

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





end end

















