function factory ()
    return function (signal, ...)
        local sel = Editor:get_selection()
        local count = 0
        local midi_region

        for r in sel.regions:regionlist():iter() do
            count = count + 1
            if r:to_audioregion():isnil() then
                local md = LuaDialog.Message ("Estimate Tempo", "The selected region is not an audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
                print (md:run())
                md = nil
                collectgarbage ()
                return
            else
                audio_region = r
            end
        end

        if count ~= 1 then
            local md = LuaDialog.Message ("Esitmate Tempo", "Please select exactly 1 audio region", LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
            print (md:run())
            md = nil
            collectgarbage ()
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

        local command = "sox  " ..quotedfilepath.. " -t raw -r 48000  -e float -c 1 - | bpm"

        os.execute(command)

        local handle = io.popen(command)
        local result = handle:read("*a")
        handle:close()

        local md = LuaDialog.Message("Estimate Tempo", result, LuaDialog.MessageType.Info, LuaDialog.ButtonType.Close)
        print(md:run())
        md = nil
        collectgarbage()

        local num = tonumber(result)

        -- to do, add tempo markers and prompt whether or not you want to tempo markers

        -- set a tempo map
        local tm = Temporal.TempoMap.write_copy ()
        tm:set_tempo (Temporal.Tempo (num, num, 4), st )
        tm:set_tempo (Temporal.Tempo (120, 120, 4), et )

        -- tm:set_tempo (Temporal.Tempo (120, 80, 4), Temporal.timepos_t.from_ticks (Temporal.ticks_per_beat * 4))

        Session:begin_reversible_command ("Change Tempo Map")
        Temporal.TempoMap.update (tm)
        if not Session:abort_empty_reversible_command () then
            Session:commit_reversible_command (nil)
        end
        tm = nil

        -- Abort Edit example
        -- after every call to Temporal.TempoMap.write_copy ()
        -- there must be a matching call to
        -- Temporal.TempoMap.update() or Temporal.TempoMap.abort_update()
        Temporal.TempoMap.write_copy()
        Temporal.TempoMap.abort_update()
    end
end
