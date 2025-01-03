ardour {
  ["type"] = "EditorAction",
  name = "Audio to MIDI",
  license = "MIT",
  author = "Ardour Team (Modified by Justin Ehrlichman)",
  description = [[
Analyze audio from the selected audio region to a selected MIDI region.

A MIDI region on the target track will have to be created first (use the pen tool).

This script uses the Polyphonic Transcription VAMP plugin from Queen Mary Univ, London.
The plugin works best at 44.1KHz input sample rate, and is tuned for piano and guitar music. Velocity is not estimated.
This version has been modified to produce both monophonic and polyphonic MIDI output.
]]
}


function factory() return function()

  local dialog_options = {
    {
      type = "dropdown", key = "dropdown", title = "Choose type of MIDI Transcription", values =
      {
        ["Monophonic (Best for voice to MIDI)"] = 1, ["Polyphonic"] = 2
      },
      default = "Monophonic (Best for voice to MIDI)"
    }
  }

  local od = LuaDialog.Dialog("Choose MIDI Transcription Type", dialog_options)
  local rv = od:run()

    if rv and rv["dropdown"] == 1 then
  local sel = Editor:get_selection()
  local sr = Session:nominal_sample_rate()
  local tm = Temporal.TempoMap.read()
  local vamp = ARDOUR.LuaAPI.Vamp("libardourvampplugins:qm-transcription", sr)
  local midi_region = nil
  local audio_regions = {}
  local start_time = Session:current_end_sample()
  local end_time = Session:current_start_sample()
  local max_pos = 0
  local cur_pos = 0

  for r in sel.regions:regionlist():iter() do
    local ar = r:to_audioregion()
    if not ar:isnil() then
      local st = r:position():samples()
      local ln = r:length():samples()
      local et = st + ln
      if st < start_time then
        start_time = st
      end
      if et > end_time then
        end_time = et
      end
      table.insert(audio_regions, ar)
      max_pos = max_pos + ar:to_readable():readable_length()
    else
      midi_region = r:to_midiregion()
    end
  end

  if #audio_regions == 0 then
    LuaDialog.Message("Monophonic Audio to MIDI",
      "No source audio region(s) selected.\nAt least one audio-region to be analyzed needs to be selected.",
      LuaDialog.MessageType.Error,
      LuaDialog.ButtonType.Close
    ):run()
    return
  end

  if not midi_region then
    LuaDialog.Message("Monophonic Audio to MIDI",
      "No target MIDI region selected.\nA MIDI region, ideally empty, and extending beyond the selected audio-region(s) needs to be selected.",
      LuaDialog.MessageType.Error,
      LuaDialog.ButtonType.Close
    ):run()
    return
  end

  midi_region:set_initial_position(Temporal.timepos_t(start_time))
  midi_region:set_length(Temporal.timecnt_t(end_time - start_time))

  local pdialog = LuaDialog.ProgressWindow("Audio to MIDI", true)
  function progress(_, pos)
    return pdialog:progress((cur_pos + pos) / max_pos, "Analyzing")
  end

  for i, ar in pairs(audio_regions) do
    local a_off = ar:position()
    local b_off = tm:quarters_at(midi_region:position())

    vamp:analyze(ar:to_readable(), 0, progress)

    if pdialog:canceled() then
      goto out
    end

    cur_pos = cur_pos + ar:to_readable():readable_length()
    pdialog:progress(cur_pos / max_pos, "Generating MIDI")

    local fl = vamp:plugin():getRemainingFeatures():at(0)
    if fl and fl:size() > 0 then
      local mm = midi_region:midi_source(0):model()
      local midi_command = mm:new_note_diff_command("Audio2Midi")

      local last_timestamp = -1 -- Keep track of last processed timestamp
      for f in fl:iter() do
        local ft = Vamp.RealTime.realTime2Frame(f.timestamp, sr)
        local fd = Vamp.RealTime.realTime2Frame(f.duration, sr)
        local fn = f.values:at(0)

        -- Process only the first note for each unique timestamp
        if ft ~= last_timestamp then
          last_timestamp = ft

          local bs = tm:quarters_at(a_off + Temporal.timecnt_t(ft), 0)
          local be = tm:quarters_at(a_off + Temporal.timecnt_t(ft + fd), 0)

          local pos = bs - b_off
          local len = be - bs
          local note = ARDOUR.LuaAPI.new_noteptr(0, pos, len, fn + 1, 0x7f)
          midi_command:add(note)
        end
      end
      mm:apply_command(Session, midi_command)
    end

    -- Reset the plugin for the next iteration
    vamp:reset()
  end

  ::out::
  pdialog:done()
  elseif rv and rv["dropdown"] == 2 then
  local sel = Editor:get_selection ()
	local sr = Session:nominal_sample_rate ()
	local tm = Temporal.TempoMap.read ()
	local vamp = ARDOUR.LuaAPI.Vamp ("libardourvampplugins:qm-transcription", sr)
	local midi_region = nil
	local audio_regions = {}
	local start_time = Session:current_end_sample ()
	local end_time = Session:current_start_sample ()
	local max_pos = 0
	local cur_pos = 0
	for r in sel.regions:regionlist ():iter () do
		local ar = r:to_audioregion()
		if not ar:isnil() then
			local st = r:position():samples()
			local ln = r:length():samples()
			local et = st + ln;
			if st < start_time then
				start_time = st
			end
			if et > end_time then
				end_time = et
			end
			table.insert(audio_regions, ar)
			max_pos = max_pos + ar:to_readable ():readable_length ()
		else
			midi_region = r:to_midiregion()
		end
	end

	if #audio_regions == 0 then
		LuaDialog.Message ("Polyphonic Audio to MIDI", "No source audio region(s) selected.\nAt least one audio-region to be analyzed need to be selected.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run ()
		return
	end
	if not midi_region then
		LuaDialog.Message ("Polyphonic Audio to MIDI", "No target MIDI region selected.\nA MIDI region, ideally empty, and extending beyond the selected audio-region(s) needs to be selected.", LuaDialog.MessageType.Error, LuaDialog.ButtonType.Close):run ()
		return
	end

	midi_region:set_initial_position (Temporal.timepos_t (start_time))
	midi_region:set_length (Temporal.timecnt_t (end_time - start_time))

	local pdialog = LuaDialog.ProgressWindow ("Audio to MIDI", true)
	function progress (_, pos)
		return pdialog:progress ((cur_pos + pos) / max_pos, "Analyzing")
	end

	for i,ar in pairs(audio_regions) do
		local a_off = ar:position ()
		local b_off = tm:quarters_at (midi_region:position ());

		vamp:analyze (ar:to_readable (), 0, progress)

		if pdialog:canceled () then
			goto out
		end

		cur_pos = cur_pos + ar:to_readable ():readable_length ()
		pdialog:progress (cur_pos / max_pos, "Generating MIDI")

		local fl = vamp:plugin ():getRemainingFeatures ():at (0)
		if fl and fl:size() > 0 then
			local mm = midi_region:midi_source(0):model()
			local midi_command = mm:new_note_diff_command ("Audio2Midi")
			for f in fl:iter () do
				local ft = Temporal.timecnt_t (Vamp.RealTime.realTime2Frame (f.timestamp, sr))
				local fd = Temporal.timecnt_t (Vamp.RealTime.realTime2Frame (f.duration, sr))
				local fn = f.values:at (0)

				local bs = tm:quarters_at (a_off + ft, 0)
				local be = tm:quarters_at (a_off + ft + fd, 0)
				print ("N", bs, be, fn + 1)

				local pos = bs - b_off
				local len = be - bs
				local note = ARDOUR.LuaAPI.new_noteptr (0, pos, len, fn + 1, 0x7f)
				midi_command:add (note)
			end
			mm:apply_command (Session, midi_command)
		end
		-- reset the plugin (prepare for next iteration)
		vamp:reset ()
	end

	::out::
	pdialog:done ();
  else
    return
  end

end end
