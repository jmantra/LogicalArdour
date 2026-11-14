-- Shared bridge for the MuseScore launcher and its sync hook.

ScoreEditor = ScoreEditor or {}
if not ScoreEditor.script_dir or ScoreEditor.script_dir == "" then
    ScoreEditor.script_dir = "."
end

function ScoreEditor.shell_quote(text)
    return "'" .. tostring(text):gsub("'", "'\\''") .. "'"
end

function ScoreEditor.ensure_dir(dir)
    os.execute("mkdir -p " .. ScoreEditor.shell_quote(dir))
end

function ScoreEditor.read_file(path)
    local file = io.open(path, "r")
    if not file then
        return nil
    end
    local text = file:read("*a")
    file:close()
    return text
end

function ScoreEditor.atomic_write(path, contents)
    local tmp = path .. ".tmp"
    local file = io.open(tmp, "w")
    if not file then
        return false
    end
    file:write(contents)
    file:close()
    os.remove(path)
    return os.rename(tmp, path)
end

function ScoreEditor.json_string(text)
    text = tostring(text or "")
    text = text:gsub("\\", "\\\\")
    text = text:gsub("\"", "\\\"")
    text = text:gsub("\n", "\\n")
    text = text:gsub("\r", "\\r")
    text = text:gsub("\t", "\\t")
    return "\"" .. text .. "\""
end

function ScoreEditor.json_number(value)
    if type(value) ~= "number" then
        return "0"
    end
    return string.format("%.6f", value)
end

function ScoreEditor.parse_json(text)
    local index = 1
    local function peek()
        return text:sub(index, index)
    end
    local function skip()
        while true do
            local char = peek()
            if char == "" or not char:match("%s") then
                break
            end
            index = index + 1
        end
    end
    local parse_value
    local function parse_string()
        index = index + 1
        local out = {}
        while true do
            local char = peek()
            if char == "" then
                return table.concat(out)
            end
            index = index + 1
            if char == "\"" then
                return table.concat(out)
            elseif char == "\\" then
                local escaped = peek()
                index = index + 1
                if escaped == "n" then
                    out[#out + 1] = "\n"
                elseif escaped == "r" then
                    out[#out + 1] = "\r"
                elseif escaped == "t" then
                    out[#out + 1] = "\t"
                else
                    out[#out + 1] = escaped
                end
            else
                out[#out + 1] = char
            end
        end
    end
    local function parse_number()
        local start = index
        while peek():match("[%d+%-eE%.]") do
            index = index + 1
        end
        return tonumber(text:sub(start, index - 1)) or 0
    end
    local function parse_object()
        local object = {}
        index = index + 1
        skip()
        if peek() == "}" then
            index = index + 1
            return object
        end
        while true do
            skip()
            local key = parse_string()
            skip()
            if peek() == ":" then
                index = index + 1
            end
            object[key] = parse_value()
            skip()
            local char = peek()
            if char == "," then
                index = index + 1
            else
                if char == "}" then
                    index = index + 1
                end
                return object
            end
        end
    end
    local function parse_array()
        local array = {}
        index = index + 1
        skip()
        if peek() == "]" then
            index = index + 1
            return array
        end
        while true do
            array[#array + 1] = parse_value()
            skip()
            local char = peek()
            if char == "," then
                index = index + 1
            else
                if char == "]" then
                    index = index + 1
                end
                return array
            end
        end
    end
    parse_value = function()
        skip()
        local char = peek()
        if char == "{" then
            return parse_object()
        elseif char == "[" then
            return parse_array()
        elseif char == "\"" then
            return parse_string()
        elseif char == "t" then
            index = index + 4
            return true
        elseif char == "f" then
            index = index + 5
            return false
        elseif char == "n" then
            index = index + 4
            return nil
        else
            return parse_number()
        end
    end
    local ok, value = pcall(parse_value)
    if not ok then
        return nil
    end
    return value
end

function ScoreEditor.to_quarters(value)
    if type(value) == "number" then
        return value
    end
    if value == nil then
        return 0
    end
    local ok, ticks = pcall(function()
        return value:to_ticks()
    end)
    if ok and type(ticks) == "number" and Temporal and Temporal.ticks_per_beat and Temporal.ticks_per_beat ~= 0 then
        return ticks / Temporal.ticks_per_beat
    end
    return 0
end

function ScoreEditor.bbt(bar, beat, ticks)
    local function filled(value)
        if value == nil then
            return nil
        end
        local ok = pcall(function()
            value.bars = bar
            value.beats = beat
            value.ticks = ticks
        end)
        if ok then
            return value
        end
        return nil
    end
    local attempts = {
        function() return Temporal.BBT_Argument(bar, beat, ticks) end,
        function() return Temporal.BBT_TIME(bar, beat, ticks) end,
        function() return Temporal.BBT_Time(bar, beat, ticks) end,
        function() return filled(Temporal.BBT_Argument()) end,
        function() return filled(Temporal.BBT_TIME()) end,
    }
    for _, attempt in ipairs(attempts) do
        local ok, value = pcall(attempt)
        if ok and value ~= nil then
            return value
        end
    end
    return nil
end

function ScoreEditor.json_int(value)
    return string.format("%.0f", math.floor(tonumber(value) or 0))
end

function ScoreEditor.file_exists(path)
    local file = io.open(path, "rb")
    if file then
        file:close()
        return true
    end
    return false
end

function ScoreEditor.find_bin()
    local home = os.getenv("HOME") or ""
    local candidates = {
        "/opt/LogicalArdour/score-editor",
        ScoreEditor.script_dir .. "/../../score-editor/target/release/score-editor",
        ScoreEditor.script_dir .. "/../../score-editor/target/debug/score-editor",
        home .. "/LogicalArdour/score-editor/target/release/score-editor",
    }
    for _, path in ipairs(candidates) do
        if ScoreEditor.file_exists(path) then
            return path
        end
    end
    return nil
end

function ScoreEditor.dialog(title, message, kind)
    if not LuaDialog then
        print(title .. ": " .. message)
        return
    end
    local message_type = LuaDialog.MessageType.Info
    if kind == "error" then
        message_type = LuaDialog.MessageType.Error
    end
    LuaDialog.Message(title, message, message_type, LuaDialog.ButtonType.Close):run()
end

function ScoreEditor.region_identity(track_id, name, samples)
    return tostring(track_id) .. "|" .. tostring(name) .. "|" .. tostring(samples)
end

function ScoreEditor.track_id_of(region)
    local ok, playlist = pcall(function()
        return region:playlist()
    end)
    if not ok or not playlist or playlist:isnil() then
        return ""
    end
    local id_ok, id = pcall(function()
        return playlist:get_orig_track_id()
    end)
    if not id_ok or id == nil then
        return ""
    end
    return tostring(id)
end

function ScoreEditor.track_name_of(region)
    local ok, playlist = pcall(function()
        return region:playlist()
    end)
    if not ok or not playlist or playlist:isnil() then
        return ""
    end
    local name_ok, name = pcall(function()
        return playlist:name()
    end)
    if name_ok and name then
        return tostring(name)
    end
    return ""
end

function ScoreEditor.each_midi_region(callback)
    if not Session then
        return
    end
    local routes = Session:get_routes()
    if not routes then
        return
    end
    for route in routes:iter() do
        local track = route:to_track()
        if track and not track:isnil() then
            local midi = track:to_midi_track()
            if midi and not midi:isnil() then
                local playlist = track:playlist()
                if playlist and not playlist:isnil() then
                    local list = playlist:region_list()
                    if list then
                        for region in list:iter() do
                            local midi_region = region:to_midiregion()
                            if midi_region and not midi_region:isnil() then
                                callback(route, midi_region)
                            end
                        end
                    end
                end
            end
        end
    end
end

function ScoreEditor.selected_midi_regions()
    local found = {}
    if not Editor then
        return found
    end
    local selection = Editor:get_selection()
    if not selection or selection:empty() then
        return found
    end
    local regions = selection.regions:regionlist()
    if not regions or regions:empty() then
        return found
    end
    for region in regions:iter() do
        local midi_region = region:to_midiregion()
        if midi_region and not midi_region:isnil() then
            found[#found + 1] = midi_region
        end
    end
    return found
end

function ScoreEditor.describe(region)
    local name = ""
    local name_ok, region_name = pcall(function()
        return region:name()
    end)
    if name_ok and region_name then
        name = tostring(region_name)
    end
    local samples = 0
    local pos_ok, position = pcall(function()
        return region:position():samples()
    end)
    if pos_ok and type(position) == "number" then
        samples = position
    end
    local track_id = ScoreEditor.track_id_of(region)
    local track_name = ScoreEditor.track_name_of(region)
    return {
        region_id = ScoreEditor.region_identity(track_id, name, samples),
        track_id = track_id,
        track_name = track_name,
        region_name = name,
        position_samples = samples,
        region = region,
    }
end

function ScoreEditor.find_described(region_id)
    local match = nil
    ScoreEditor.each_midi_region(function(_, region)
        local described = ScoreEditor.describe(region)
        if described.region_id == region_id then
            match = described
        end
    end)
    return match
end

function ScoreEditor.session_key()
    if not Session then
        return ""
    end
    local text = ScoreEditor.read_file(Session:path() .. "/key.txt") or ""
    return (text:gsub("^%s+", ""):gsub("%s+$", ""))
end

function ScoreEditor.suggest_percussion(name)
    local lower = string.lower(name or "")
    return lower:find("drum", 1, true) ~= nil or lower:find("perc", 1, true) ~= nil
end

function ScoreEditor.read_notes(region)
    local notes = {}
    local warnings = {}
    local ok, model = pcall(function()
        return region:midi_source(0):model()
    end)
    if not ok or not model or (model.isnil and model:isnil()) then
        warnings[#warnings + 1] = "This region has no MIDI source."
        return notes, warnings
    end
    local list_ok, list = pcall(function()
        return ARDOUR.LuaAPI.note_list(model)
    end)
    if not list_ok or not list then
        warnings[#warnings + 1] = "The MIDI notes in this region could not be read."
        return notes, warnings
    end
    for note in list:iter() do
        local note_ok, encoded = pcall(function()
            return {
                channel = note:channel() or 0,
                time = ScoreEditor.to_quarters(note:time()),
                length = ScoreEditor.to_quarters(note:length()),
                pitch = note:note() or 0,
                velocity = note:velocity() or 80,
            }
        end)
        if note_ok and encoded then
            notes[#notes + 1] = encoded
        end
    end
    return notes, warnings
end

function ScoreEditor.collect_bars(region)
    local bars = {}
    local origin = 0
    local length = 0
    if not Temporal or not Temporal.TempoMap then
        return bars, origin, length
    end
    local map = Temporal.TempoMap.read()
    local region_start = region:position()
    local region_end = region_start + region:length()
    origin = ScoreEditor.to_quarters(map:quarters_at(region_start))
    local end_quarters = ScoreEditor.to_quarters(map:quarters_at(region_end))
    length = end_quarters - origin
    local bbt = map:bbt_at(region_start)
    local bar = (bbt and bbt.bars) or 1
    if bar < 1 then
        bar = 1
    end
    local guard = 0
    while guard < 4000 do
        guard = guard + 1
        local at = ScoreEditor.bbt(bar, 1, 0)
        local nxt = ScoreEditor.bbt(bar + 1, 1, 0)
        if not at or not nxt then
            break
        end
        local start_quarters = ScoreEditor.to_quarters(map:quarters_at_bbt(at))
        local next_quarters = ScoreEditor.to_quarters(map:quarters_at_bbt(nxt))
        if next_quarters <= origin + 0.0001 then
            bar = bar + 1
        elseif start_quarters >= end_quarters - 0.0001 then
            break
        else
            local meter = map:meter_at_bbt(at)
            local tempo = map:tempo_at_bbt(at)
            bars[#bars + 1] = {
                bar = bar,
                numerator = meter:divisions_per_bar(),
                denominator = meter:note_value(),
                bpm = tempo:quarter_notes_per_minute(),
                start_quarters = start_quarters - origin,
            }
            if next_quarters <= start_quarters then
                break
            end
            bar = bar + 1
        end
    end
    return bars, origin, length
end

function ScoreEditor.hash_score(notes, bars)
    local hash = 2166136261
    local function mix(value)
        local number = math.floor(tonumber(value) or 0)
        hash = (hash * 16777619 + (number % 4294967296)) % 4294967296
    end
    mix(#notes)
    for _, note in ipairs(notes) do
        mix(note.channel)
        mix((note.time or 0) * 1000)
        mix((note.length or 0) * 1000)
        mix(note.pitch)
        mix(note.velocity)
    end
    mix(#bars)
    for _, bar in ipairs(bars) do
        mix(bar.bar)
        mix(bar.numerator)
        mix(bar.denominator)
        mix((bar.bpm or 0) * 100)
        mix((bar.start_quarters or 0) * 1000)
    end
    hash = math.floor(hash) % 4294967296
    local digits = "0123456789abcdef"
    local out = {}
    for place = 8, 1, -1 do
        local digit = hash % 16
        out[place] = digits:sub(digit + 1, digit + 1)
        hash = math.floor(hash / 16)
    end
    return table.concat(out)
end

function ScoreEditor.encode_score(described, notes, bars, warnings, length)
    local parts = { "{\n" }
    local function field(name, value, comma)
        parts[#parts + 1] = "  " .. ScoreEditor.json_string(name) .. ": " .. value
        if comma then
            parts[#parts + 1] = ",\n"
        else
            parts[#parts + 1] = "\n"
        end
    end
    field("region_id", ScoreEditor.json_string(described.region_id), true)
    field("track_id", ScoreEditor.json_string(described.track_id), true)
    field("track_name", ScoreEditor.json_string(described.track_name), true)
    field("region_name", ScoreEditor.json_string(described.region_name), true)
    field("position_samples", ScoreEditor.json_int(described.position_samples), true)
    field("session_key", ScoreEditor.json_string(ScoreEditor.session_key()), true)
    field("content_hash", ScoreEditor.json_string(ScoreEditor.hash_score(notes, bars)), true)
    field("suggest_percussion", ScoreEditor.suggest_percussion(described.track_name) and "true" or "false", true)
    field("region_length_quarters", ScoreEditor.json_number(length or 0), true)
    parts[#parts + 1] = "  \"notes\": [\n"
    for index, note in ipairs(notes) do
        parts[#parts + 1] = "    {"
        parts[#parts + 1] = "\"channel\": " .. ScoreEditor.json_int(note.channel) .. ", "
        parts[#parts + 1] = "\"time\": " .. ScoreEditor.json_number(note.time) .. ", "
        parts[#parts + 1] = "\"length\": " .. ScoreEditor.json_number(note.length) .. ", "
        parts[#parts + 1] = "\"pitch\": " .. ScoreEditor.json_int(note.pitch) .. ", "
        parts[#parts + 1] = "\"velocity\": " .. ScoreEditor.json_int(note.velocity or 80)
        parts[#parts + 1] = index == #notes and "}\n" or "},\n"
    end
    parts[#parts + 1] = "  ],\n  \"bars\": [\n"
    for index, bar in ipairs(bars) do
        parts[#parts + 1] = "    {"
        parts[#parts + 1] = "\"bar\": " .. ScoreEditor.json_int(bar.bar or 1) .. ", "
        parts[#parts + 1] = "\"numerator\": " .. ScoreEditor.json_int(bar.numerator or 4) .. ", "
        parts[#parts + 1] = "\"denominator\": " .. ScoreEditor.json_int(bar.denominator or 4) .. ", "
        parts[#parts + 1] = "\"bpm\": " .. ScoreEditor.json_number(bar.bpm or 120) .. ", "
        parts[#parts + 1] = "\"start_quarters\": " .. ScoreEditor.json_number(bar.start_quarters or 0)
        parts[#parts + 1] = index == #bars and "}\n" or "},\n"
    end
    parts[#parts + 1] = "  ],\n  \"warnings\": [\n"
    for index, warning in ipairs(warnings) do
        parts[#parts + 1] = "    " .. ScoreEditor.json_string(warning)
        parts[#parts + 1] = index == #warnings and "\n" or ",\n"
    end
    parts[#parts + 1] = "  ]\n}\n"
    return table.concat(parts)
end

function ScoreEditor.to_ticks(value)
    if type(value) == "number" then
        local per_beat = (Temporal and Temporal.ticks_per_beat) or 1920
        return math.floor(value * per_beat + 0.5)
    end
    if value == nil then
        return nil
    end
    local ok, ticks = pcall(function()
        return value:to_ticks()
    end)
    if ok and type(ticks) == "number" then
        return ticks
    end
    return nil
end

function ScoreEditor.beats_from_quarters(quarters)
    if not Temporal or not Temporal.ticks_per_beat or Temporal.ticks_per_beat == 0 then
        return nil
    end
    local ticks = ScoreEditor.to_ticks(tonumber(quarters) or 0)
    local attempts = {
        function() return Temporal.Beats.from_ticks(ticks) end,
        function() return Temporal.Beats(ticks) end,
        function() return Temporal.Beats.new(ticks) end,
    }
    for _, attempt in ipairs(attempts) do
        local ok, value = pcall(attempt)
        if ok and value ~= nil and ScoreEditor.to_ticks(value) ~= nil then
            return value
        end
    end
    return nil
end

function ScoreEditor.same_time(beats, quarters)
    local ticks = ScoreEditor.to_ticks(beats)
    local wanted = ScoreEditor.to_ticks(tonumber(quarters) or 0)
    if ticks == nil or wanted == nil then
        return false
    end
    local delta = ticks - wanted
    if delta < 0 then
        delta = -delta
    end
    return delta <= 1
end

function ScoreEditor.agent_log(hypothesis, message, data)
    -- #region agent log
    local file = io.open("/home/justin/LogicalArdour/.cursor/debug-d1f321.log", "a")
    if not file then
        return
    end
    file:write(string.format(
        "{\"sessionId\":\"d1f321\",\"runId\":\"run1\",\"hypothesisId\":%s,\"location\":\"score_editor_common.lua\",\"message\":%s,\"data\":%s,\"timestamp\":%d}\n",
        ScoreEditor.json_string(hypothesis or ""),
        ScoreEditor.json_string(message or ""),
        data or "{}",
        (os.time() or 0) * 1000
    ))
    file:close()
    -- #endregion
end

function ScoreEditor.mscore_dir()
    local base = os.getenv("XDG_RUNTIME_DIR")
    if not base or base == "" then
        base = "/tmp"
    end
    return base .. "/logicalardour-mscore"
end

function ScoreEditor.encode_note_file(notes, revision, origin, region_id)
    local parts = { "{\n" }
    parts[#parts + 1] = "  \"revision\": " .. ScoreEditor.json_int(revision or 0) .. ",\n"
    parts[#parts + 1] = "  \"written\": " .. ScoreEditor.json_int(os.time()) .. ",\n"
    parts[#parts + 1] = "  \"origin\": " .. ScoreEditor.json_string(origin or "") .. ",\n"
    parts[#parts + 1] = "  \"region_id\": " .. ScoreEditor.json_string(region_id or "") .. ",\n"
    parts[#parts + 1] = "  \"notes\": [\n"
    for index, note in ipairs(notes or {}) do
        parts[#parts + 1] = "    {"
        parts[#parts + 1] = "\"channel\": " .. ScoreEditor.json_int(note.channel) .. ", "
        parts[#parts + 1] = "\"time\": " .. ScoreEditor.json_number(note.time) .. ", "
        parts[#parts + 1] = "\"length\": " .. ScoreEditor.json_number(note.length) .. ", "
        parts[#parts + 1] = "\"pitch\": " .. ScoreEditor.json_int(note.pitch) .. ", "
        parts[#parts + 1] = "\"velocity\": " .. ScoreEditor.json_int(note.velocity or 80)
        parts[#parts + 1] = index == #notes and "}\n" or "},\n"
    end
    parts[#parts + 1] = "  ]\n}\n"
    return table.concat(parts)
end

function ScoreEditor.read_note_file(path)
    local text = ScoreEditor.read_file(path)
    if not text then
        return nil
    end
    local parsed = ScoreEditor.parse_json(text)
    if type(parsed) ~= "table" then
        return nil
    end
    parsed.notes = parsed.notes or {}
    parsed.revision = tonumber(parsed.revision) or 0
    return parsed
end

function ScoreEditor.mscore_plugin_alive(dir)
    local stamp = tonumber(ScoreEditor.read_file(dir .. "/heartbeat"))
    if not stamp or not os.time then
        return false
    end
    local delta = os.time() - stamp
    if delta < 0 then
        delta = -delta
    end
    return delta <= 5
end

function ScoreEditor.install_mscore_plugin()
    local home = os.getenv("HOME") or ""
    local candidates = {
        ScoreEditor.script_dir .. "/../../musescore/logicalardour-sync.qml",
        home .. "/LogicalArdour/musescore/logicalardour-sync.qml",
        "/opt/LogicalArdour/logicalardour-sync.qml",
    }
    local source = nil
    for _, path in ipairs(candidates) do
        if ScoreEditor.file_exists(path) then
            source = path
            break
        end
    end
    if not source then
        return false
    end
    local text = ScoreEditor.read_file(source)
    if not text then
        return false
    end
    local dest_dir = home .. "/Documents/MuseScore3/Plugins"
    ScoreEditor.ensure_dir(dest_dir)
    return ScoreEditor.atomic_write(dest_dir .. "/logicalardour-sync.qml", text)
end

function ScoreEditor.export_musicxml(bin, score_path, xml_path)
    local command = ScoreEditor.shell_quote(bin)
        .. " --musicxml "
        .. ScoreEditor.shell_quote(score_path)
        .. " "
        .. ScoreEditor.shell_quote(xml_path)
    local ok = os.execute(command)
    return ok == true or ok == 0
end

function ScoreEditor.open_in_musescore()
    local selected = ScoreEditor.selected_midi_regions()
    if #selected ~= 1 then
        ScoreEditor.dialog("MuseScore", "Select exactly one MIDI region.", "error")
        return
    end
    local described = ScoreEditor.describe(selected[1])
    local dir = ScoreEditor.mscore_dir()
    ScoreEditor.ensure_dir(dir)
    ScoreEditor.atomic_write("/tmp/logicalardour-mscore-dir", dir .. "\n")
    local notes, warnings = ScoreEditor.read_notes(described.region)
    ScoreEditor.agent_log("B", "opened bridge", "{\"dir\":" .. ScoreEditor.json_string(dir) .. ",\"region\":" .. ScoreEditor.json_string(described.region_id) .. ",\"notes\":" .. tostring(#notes) .. "}")
    local bars, _, length = ScoreEditor.collect_bars(described.region)
    local score_path = dir .. "/score.json"
    local xml_path = dir .. "/region.musicxml"
    ScoreEditor.atomic_write(score_path, ScoreEditor.encode_score(described, notes, bars, warnings, length))
    ScoreEditor.atomic_write(dir .. "/ardour-notes.json", ScoreEditor.encode_note_file(notes, 1, "ardour", described.region_id))
    ScoreEditor.atomic_write(dir .. "/active.json", "{\n  \"region_id\": " .. ScoreEditor.json_string(described.region_id) .. "\n}\n")
    local bin = ScoreEditor.find_bin()
    if not bin then
        ScoreEditor.dialog("MuseScore", "The score editor program was not found, so the live MusicXML file could not be written.", "error")
        return
    end
    if not ScoreEditor.export_musicxml(bin, score_path, xml_path) or not ScoreEditor.file_exists(xml_path) then
        ScoreEditor.dialog("MuseScore", "Could not write the MusicXML file for this region.", "error")
        return
    end
    ScoreEditor.install_mscore_plugin()
    local mscore = "/opt/LogicalArdour/mscore"
    if not ScoreEditor.file_exists(mscore) then
        mscore = "mscore"
    end
    local script = dir .. "/open-mscore.sh"
    ScoreEditor.atomic_write(script, "#!/bin/sh\nexec " .. ScoreEditor.shell_quote(mscore) .. " " .. ScoreEditor.shell_quote(xml_path) .. "\n")
    os.execute("chmod +x " .. ScoreEditor.shell_quote(script))
    os.forkexec("/bin/bash", script)
    os.execute("sleep 2")
    ScoreEditor.connect_mscore_jack(described.region)
    if not ScoreEditor.mscore_plugin_alive(dir) then
        ScoreEditor.dialog("MuseScore", "In MuseScore, run Plugins → LogicalArdour sync once and leave it open. Playback still uses JACK. Note moves travel through that plugin.", "info")
    end
end

function ScoreEditor.connect_mscore_jack(region)
    local track_id = nil
    pcall(function()
        track_id = region:playlist():get_orig_track_id()
    end)
    if track_id == nil or not Session then
        return
    end
    local selected = nil
    pcall(function()
        selected = Session:route_by_id(track_id)
    end)
    if not selected or (selected.isnil and selected:isnil()) then
        return
    end
    local destination = nil
    pcall(function()
        destination = selected:input():midi(0)
    end)
    pcall(function()
        for route in Session:get_routes():iter() do
            if not route:to_track():isnil() and not route:to_track():to_midi_track():isnil() then
                route:input():midi(0):disconnect("mscore:mscore-midi-1")
            end
        end
    end)
    if destination then
        pcall(function()
            destination:connect("mscore:mscore-midi-1")
        end)
    end
end

function ScoreEditor.apply_note_patch(described, patch)
    local removes = patch.remove or {}
    local adds = patch.add or {}
    if #removes == 0 and #adds == 0 then
        return true
    end
    local region = described and described.region
    if not region then
        return false
    end
    local model_ok, model = pcall(function()
        return region:midi_source(0):model()
    end)
    if not model_ok or not model or (model.isnil and model:isnil()) then
        return false
    end
    local list_ok, list = pcall(function()
        return ARDOUR.LuaAPI.note_list(model)
    end)
    if not list_ok or not list then
        return false
    end
    local command_ok, diff = pcall(function()
        return model:new_note_diff_command("MuseScore sync")
    end)
    if not command_ok or not diff then
        return false
    end
    local pending = {}
    for note in list:iter() do
        pending[#pending + 1] = note
    end
    for _, spec in ipairs(removes) do
        for index, note in ipairs(pending) do
            local match = false
            pcall(function()
                match = note:channel() == math.floor(tonumber(spec.channel) or 0)
                    and note:note() == math.floor(tonumber(spec.pitch) or -1)
                    and ScoreEditor.same_time(note:time(), spec.time)
                    and ScoreEditor.same_time(note:length(), spec.length)
            end)
            if match then
                diff:remove(note)
                table.remove(pending, index)
                break
            end
        end
    end
    for _, spec in ipairs(adds) do
        local onset = ScoreEditor.beats_from_quarters(spec.time)
        local length = ScoreEditor.beats_from_quarters(spec.length)
        if onset and length then
            local pitch = math.max(0, math.min(127, math.floor(tonumber(spec.pitch) or 60)))
            local channel = math.floor(tonumber(spec.channel) or 0)
            local velocity = math.max(1, math.min(127, math.floor(tonumber(spec.velocity) or 80)))
            diff:add(ARDOUR.LuaAPI.new_noteptr(channel, onset, length, pitch, velocity))
        end
    end
    local applied = pcall(function()
        model:apply_command(Session, diff)
    end)
    return applied
end

function ScoreEditor.mscore_sync_tick(state)
    local dir = ScoreEditor.mscore_dir()
    state.log_tick = (state.log_tick or 0) + 1
    local alive = ScoreEditor.mscore_plugin_alive(dir)
    if state.log_tick % 20 == 1 then
        local mscore_peek = ScoreEditor.read_note_file(dir .. "/mscore-notes.json")
        ScoreEditor.agent_log("C", "hook tick", "{\"alive\":" .. (alive and "true" or "false") .. ",\"dir\":" .. ScoreEditor.json_string(dir) .. ",\"mscoreRev\":" .. tostring(mscore_peek and mscore_peek.revision or -1) .. ",\"origin\":" .. ScoreEditor.json_string(mscore_peek and mscore_peek.origin or "") .. ",\"seen\":" .. tostring(state.seen_mscore or -1) .. "}")
    end
    if not alive then
        return
    end
    local active = ScoreEditor.parse_json(ScoreEditor.read_file(dir .. "/active.json") or "")
    if type(active) ~= "table" or not active.region_id or active.region_id == "" then
        ScoreEditor.agent_log("C", "no active region", "{\"dir\":" .. ScoreEditor.json_string(dir) .. "}")
        return
    end
    local described = ScoreEditor.find_described(active.region_id)
    if not described then
        ScoreEditor.agent_log("C", "region not found", "{\"id\":" .. ScoreEditor.json_string(active.region_id) .. "}")
        return
    end
    local notes = ScoreEditor.read_notes(described.region)
    local hash = ScoreEditor.hash_score(notes, {})
    if not state.ready then
        local existing = ScoreEditor.read_note_file(dir .. "/ardour-notes.json")
        state.seen_mscore = -1
        state.ready = true
        local file_hash = existing and ScoreEditor.hash_score(existing.notes or {}, {}) or nil
        if existing and file_hash == hash then
            state.revision = existing.revision
            state.written = tonumber(existing.written) or 0
            state.hash = hash
        else
            state.revision = (existing and existing.revision or 0) + 1
            state.hash = hash
            state.written = os.time()
            ScoreEditor.atomic_write(dir .. "/ardour-notes.json", ScoreEditor.encode_note_file(notes, state.revision, "ardour", described.region_id))
        end
    end
    local mscore = ScoreEditor.read_note_file(dir .. "/mscore-notes.json")
    local mscore_new = mscore and mscore.origin == "mscore" and mscore.revision ~= state.seen_mscore
    local region_new = hash ~= state.hash
    if mscore_new and region_new and (tonumber(mscore.written) or 0) < (state.written or 0) then
        state.seen_mscore = mscore.revision
        mscore_new = false
    end
    local mscore_wins = mscore_new
    if mscore_wins then
        local bin = ScoreEditor.find_bin()
        local patch_path = dir .. "/patch.json"
        local applied = false
        if bin then
            local command = ScoreEditor.shell_quote(bin)
                .. " --pair "
                .. ScoreEditor.shell_quote(dir .. "/ardour-notes.json")
                .. " "
                .. ScoreEditor.shell_quote(dir .. "/mscore-notes.json")
                .. " "
                .. ScoreEditor.shell_quote(patch_path)
            local ran = os.execute(command)
            if ran == true or ran == 0 then
                local patch = ScoreEditor.parse_json(ScoreEditor.read_file(patch_path) or "")
                if type(patch) == "table" then
                    applied = ScoreEditor.apply_note_patch(described, patch)
                end
            end
        end
        ScoreEditor.agent_log("D", "apply mscore revision", "{\"applied\":" .. (applied and "true" or "false") .. ",\"bin\":" .. ScoreEditor.json_string(bin or "") .. ",\"revision\":" .. tostring(mscore.revision) .. ",\"notes\":" .. tostring(mscore.notes and #mscore.notes or 0) .. "}")
        if not applied then
            return
        end
        state.seen_mscore = mscore.revision
        notes = ScoreEditor.read_notes(described.region)
        hash = ScoreEditor.hash_score(notes, {})
        state.revision = mscore.revision
        state.hash = hash
        state.written = os.time()
        ScoreEditor.atomic_write(dir .. "/ardour-notes.json", ScoreEditor.encode_note_file(notes, state.revision, "mscore", described.region_id))
        return
    end
    if region_new then
        state.revision = (state.revision or 0) + 1
        state.hash = hash
        state.written = os.time()
        ScoreEditor.atomic_write(dir .. "/ardour-notes.json", ScoreEditor.encode_note_file(notes, state.revision, "ardour", described.region_id))
    end
end
