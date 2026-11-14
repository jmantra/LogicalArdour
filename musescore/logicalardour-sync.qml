import QtQuick 2.0
import MuseScore 3.0
import FileIO 3.0

MuseScore {
    menuPath: "Plugins.LogicalArdour sync"
    description: "Keep sounding notes aligned with the open Ardour MIDI region."
    version: "1.0"
    pluginType: "dialog"
    requiresScore: true
    width: 440
    height: 180

    property string statusMessage: "LogicalArdour is watching this score. Leave this window open."
    property int seenArdour: -1
    property int ownRevision: 0
    property string fingerprint: ""
    property bool busy: false

    FileIO {
        id: bridgeFile
    }

    FileIO {
        id: logFile
    }

    function agentLog(hypothesisId, message, data) {
        // #region agent log
        var payload = JSON.stringify({
            sessionId: "d1f321",
            runId: "run1",
            hypothesisId: hypothesisId,
            location: "logicalardour-sync.qml",
            message: message,
            data: data || {},
            timestamp: Date.now()
        })
        try {
            var xhr = new XMLHttpRequest()
            xhr.open("POST", "http://127.0.0.1:7879/ingest/2d0f0e7e-1d81-49be-a049-68e4c5e7dc8f", false)
            xhr.setRequestHeader("Content-Type", "application/json")
            xhr.setRequestHeader("X-Debug-Session-Id", "d1f321")
            xhr.send(payload)
        } catch (ignored) {
        }
        try {
            var path = "/home/justin/LogicalArdour/.cursor/debug-d1f321.log"
            logFile.source = path
            var prev = ""
            try {
                prev = logFile.read() || ""
            } catch (ignoredRead) {
                prev = ""
            }
            if (prev.length > 0 && prev.charAt(prev.length - 1) !== "\n") {
                prev += "\n"
            }
            logFile.write(prev + payload + "\n")
        } catch (ignoredWrite) {
        }
        // #endregion
    }

    Timer {
        id: pulse
        interval: 400
        repeat: true
        running: false
        onTriggered: exchange()
    }

    onRun: {
        agentLog("A", "plugin started", {})
        statusMessage = "Sync started. Leave this window open."
        pulse.start()
    }

    Text {
        anchors.fill: parent
        anchors.margins: 16
        wrapMode: Text.WordWrap
        text: statusMessage
    }

    function bridgeDir() {
        bridgeFile.source = "/tmp/logicalardour-mscore-dir"
        var text = bridgeFile.read()
        if (!text) {
            return ""
        }
        return ("" + text).replace(/^\s+|\s+$/g, "")
    }

    function readText(path) {
        bridgeFile.source = path
        var text = bridgeFile.read()
        return text ? ("" + text) : ""
    }

    function writeText(path, text) {
        bridgeFile.source = path
        bridgeFile.write(text)
    }

    function decode(text) {
        if (!text || typeof JSON === "undefined" || !JSON.parse) {
            return null
        }
        try {
            return JSON.parse(text)
        } catch (error) {
            return null
        }
    }

    function encode(value) {
        if (typeof JSON !== "undefined" && JSON.stringify) {
            return JSON.stringify(value)
        }
        return "{}"
    }

    function near(left, right) {
        return Math.abs(left - right) <= 0.01
    }

    function round6(value) {
        return Math.round((value || 0) * 1000000) / 1000000
    }

    function sameSound(left, right) {
        return left.channel === right.channel
            && left.pitch === right.pitch
            && left.velocity === right.velocity
            && near(left.time, right.time)
            && near(left.length, right.length)
    }

    function isChord(element) {
        return element && typeof Element !== "undefined" && element.type === Element.CHORD
    }

    function tiedBack(note) {
        var tie = note ? note.tieBack : null
        if (!tie) {
            return false
        }
        return !!(tie.startNote || tie.endNote)
    }

    function quartersOf(chord, division) {
        var duration = chord ? chord.duration : null
        if (duration && duration.ticks) {
            return duration.ticks / division
        }
        if (duration && duration.numerator && duration.denominator) {
            return 4 * duration.numerator / duration.denominator
        }
        return 1
    }

    function velocityOf(note) {
        var value = note ? note.veloOffset : 0
        if ((note.veloType === 1 || (typeof Note !== "undefined" && note.veloType === Note.USER_VAL)) && value >= 1 && value <= 127) {
            return value
        }
        return 80
    }

    function channelFor(time, length, pitch, ardourNotes) {
        var notes = ardourNotes || []
        var i
        for (i = 0; i < notes.length; i++) {
            if (notes[i].pitch === pitch && near(notes[i].time, time) && near(notes[i].length, length)) {
                return notes[i].channel
            }
        }
        var found = -1
        for (i = 0; i < notes.length; i++) {
            if (notes[i].pitch === pitch) {
                if (found !== -1 && found !== notes[i].channel) {
                    return 0
                }
                found = notes[i].channel
            }
        }
        return found === -1 ? 0 : found
    }

    function extendPrevious(items, staff, voice, pitch, quarters) {
        var i
        for (i = items.length - 1; i >= 0; i--) {
            if (items[i].staff === staff && items[i].voice === voice && items[i].pitch === pitch) {
                items[i].length = items[i].length + quarters
                return
            }
        }
    }

    function soundingNotes(ardourNotes) {
        var items = []
        if (!curScore) {
            return items
        }
        var staves = curScore.nstaves || 1
        var division = curScore.division || 480
        var staff
        var voice
        for (staff = 0; staff < staves; staff++) {
            for (voice = 0; voice < 4; voice++) {
                var cursor = curScore.newCursor()
                cursor.staffIdx = staff
                cursor.voice = voice
                cursor.track = staff * 4 + voice
                cursor.rewind(0)
                var guard = 0
                while (cursor.segment && guard < 20000) {
                    guard = guard + 1
                    var element = cursor.element
                    if (isChord(element)) {
                        var quarters = quartersOf(element, division)
                        var start = (cursor.tick || 0) / division
                        var notes = element.notes || []
                        var index
                        for (index = 0; index < notes.length; index++) {
                            var note = notes[index]
                            if (tiedBack(note)) {
                                extendPrevious(items, staff, voice, note.pitch, quarters)
                            } else {
                                items.push({
                                    staff: staff,
                                    voice: voice,
                                    channel: channelFor(start, quarters, note.pitch, ardourNotes),
                                    time: start,
                                    length: quarters,
                                    pitch: note.pitch,
                                    velocity: velocityOf(note),
                                    element: note,
                                    chord: element
                                })
                            }
                        }
                    }
                    cursor.next()
                }
            }
        }
        return items
    }

    function publishable(items) {
        var notes = []
        var i
        for (i = 0; i < items.length; i++) {
            notes.push({
                channel: items[i].channel,
                time: round6(items[i].time),
                length: round6(items[i].length),
                pitch: items[i].pitch,
                velocity: items[i].velocity
            })
        }
        return notes
    }

    function fingerprintOf(notes) {
        var parts = []
        var i
        for (i = 0; i < notes.length; i++) {
            var note = notes[i]
            parts.push(note.channel + ":" + round6(note.time) + ":" + round6(note.length) + ":" + note.pitch + ":" + note.velocity)
        }
        parts.sort()
        return parts.join("|")
    }

    function notesMatch(current, desired) {
        if (!desired) {
            return false
        }
        if (current.length !== desired.length) {
            return false
        }
        var used = []
        var i
        var j
        for (j = 0; j < desired.length; j++) {
            used.push(false)
        }
        for (i = 0; i < current.length; i++) {
            var found = false
            for (j = 0; j < desired.length; j++) {
                if (!used[j] && sameSound(current[i], desired[j])) {
                    used[j] = true
                    found = true
                    break
                }
            }
            if (!found) {
                return false
            }
        }
        return true
    }

    function classify(current, desired) {
        var usedC = []
        var usedD = []
        var i
        var j
        for (i = 0; i < current.length; i++) {
            usedC.push(false)
        }
        for (j = 0; j < desired.length; j++) {
            usedD.push(false)
        }
        for (i = 0; i < current.length; i++) {
            for (j = 0; j < desired.length; j++) {
                if (!usedD[j] && sameSound(current[i], desired[j])) {
                    usedC[i] = true
                    usedD[j] = true
                    break
                }
            }
        }
        var retune = []
        for (i = 0; i < current.length; i++) {
            if (usedC[i]) {
                continue
            }
            for (j = 0; j < desired.length; j++) {
                if (usedD[j]) {
                    continue
                }
                if (current[i].channel === desired[j].channel && near(current[i].time, desired[j].time) && near(current[i].length, desired[j].length)) {
                    usedC[i] = true
                    usedD[j] = true
                    retune.push({ item: current[i], desired: desired[j] })
                    break
                }
            }
        }
        var candidates = []
        for (i = 0; i < current.length; i++) {
            if (usedC[i]) {
                continue
            }
            for (j = 0; j < desired.length; j++) {
                if (!usedD[j] && current[i].channel === desired[j].channel && current[i].pitch === desired[j].pitch) {
                    candidates.push({ delta: Math.abs(current[i].time - desired[j].time), i: i, j: j })
                }
            }
        }
        candidates.sort(function (left, right) { return left.delta - right.delta })
        var replace = []
        var pair
        for (i = 0; i < candidates.length; i++) {
            pair = candidates[i]
            if (usedC[pair.i] || usedD[pair.j]) {
                continue
            }
            usedC[pair.i] = true
            usedD[pair.j] = true
            replace.push({ item: current[pair.i], desired: desired[pair.j] })
        }
        var remove = []
        var add = []
        for (i = 0; i < current.length; i++) {
            if (!usedC[i]) {
                remove.push(current[i])
            }
        }
        for (j = 0; j < desired.length; j++) {
            if (!usedD[j]) {
                add.push(desired[j])
            }
        }
        return { retune: retune, replace: replace, remove: remove, add: add }
    }

    function setVelocity(note, velocity) {
        if (!note) {
            return
        }
        note.veloType = 1
        note.veloOffset = velocity
    }

    function removeSounding(item) {
        var note = item.element
        var chord = item.chord
        if (chord && chord.remove) {
            chord.remove(note)
            return
        }
        if (note && note.parent && note.parent.remove) {
            note.parent.remove(note)
            return
        }
        if (curScore.selection && note) {
            curScore.selection.select(note)
            cmd("delete")
        }
    }

    function setLength(cursor, quarters) {
        var choices = [
            [4, 1, 1],
            [2, 1, 2],
            [1.5, 3, 8],
            [1, 1, 4],
            [0.75, 3, 16],
            [0.5, 1, 8],
            [0.375, 3, 32],
            [0.25, 1, 16],
            [0.125, 1, 32]
        ]
        var best = choices[3]
        var bestDelta = 100
        var i
        for (i = 0; i < choices.length; i++) {
            var delta = Math.abs(choices[i][0] - quarters)
            if (delta < bestDelta) {
                bestDelta = delta
                best = choices[i]
            }
        }
        cursor.setDuration(best[1], best[2])
    }

    function addSounding(staff, voice, desired) {
        var division = curScore.division || 480
        var target = Math.round((desired.time || 0) * division)
        var cursor = curScore.newCursor()
        cursor.staffIdx = staff
        cursor.voice = voice
        cursor.track = staff * 4 + voice
        cursor.rewind(0)
        if (cursor.rewindToTick) {
            cursor.rewindToTick(target)
        } else {
            var guard = 0
            while (cursor.segment && cursor.tick < target && guard < 20000) {
                cursor.next()
                guard = guard + 1
            }
        }
        setLength(cursor, desired.length || 1)
        cursor.addNote(desired.pitch, false)
        var chord = cursor.element
        if (chord && chord.notes && chord.notes.length > 0) {
            var note = chord.notes[chord.notes.length - 1]
            var n
            for (n = 0; n < chord.notes.length; n++) {
                if (chord.notes[n].pitch === desired.pitch) {
                    note = chord.notes[n]
                }
            }
            setVelocity(note, desired.velocity || 80)
        }
    }

    function applyPlan(plan) {
        curScore.startCmd()
        var i
        for (i = 0; i < plan.retune.length; i++) {
            var retune = plan.retune[i]
            if (retune.item.element) {
                retune.item.element.pitch = retune.desired.pitch
                setVelocity(retune.item.element, retune.desired.velocity || 80)
            }
        }
        for (i = 0; i < plan.replace.length; i++) {
            removeSounding(plan.replace[i].item)
        }
        for (i = 0; i < plan.remove.length; i++) {
            removeSounding(plan.remove[i])
        }
        for (i = 0; i < plan.replace.length; i++) {
            var moved = plan.replace[i]
            addSounding(moved.item.staff, moved.item.voice, moved.desired)
        }
        for (i = 0; i < plan.add.length; i++) {
            addSounding(0, 0, plan.add[i])
        }
        curScore.endCmd()
    }

    function writeNotes(dir, notes, revision, origin, regionId) {
        writeText(dir + "/mscore-notes.json", encode({
            revision: revision,
            written: Math.floor(Date.now() / 1000),
            origin: origin,
            region_id: regionId || "",
            notes: notes
        }))
    }

    function exchange() {
        if (busy) {
            return
        }
        busy = true
        try {
            exchangeOnce()
        } catch (error) {
            agentLog("A", "exchange failed", { error: "" + error })
            statusMessage = "Sync hit a problem and will try again."
        }
        busy = false
    }

    function exchangeOnce() {
        var dir = bridgeDir()
        if (!dir) {
            if (!exchangeOnce.logged) {
                exchangeOnce.logged = true
                agentLog("B", "no bridge dir", { dir: "" })
            }
            statusMessage = "Open a MIDI region from Ardour, then leave this window open."
            busy = false
            return
        }
        writeText(dir + "/heartbeat", "" + Math.floor(Date.now() / 1000) + "\n")
        var ardour = decode(readText(dir + "/ardour-notes.json"))
        var current = soundingNotes(ardour ? ardour.notes : [])
        var clean = publishable(current)
        var print = fingerprintOf(clean)
        if (!exchangeOnce.logged) {
            exchangeOnce.logged = true
            agentLog("B", "first exchange", {
                dir: dir,
                notes: clean.length,
                ardourOrigin: ardour ? ardour.origin : "",
                ardourRevision: ardour ? ardour.revision : -1
            })
        }
        if (ardour && ardour.origin === "ardour" && ardour.revision !== seenArdour) {
            var regionId = ardour.region_id || ""
            if (notesMatch(clean, ardour.notes || [])) {
                seenArdour = ardour.revision
                ownRevision = ardour.revision
                writeNotes(dir, clean, ownRevision, "ardour", regionId)
                fingerprint = print
                statusMessage = "Score matches Ardour."
                busy = false
                return
            }
            applyPlan(classify(current, ardour.notes || []))
            seenArdour = ardour.revision
            ownRevision = ardour.revision
            current = soundingNotes(ardour.notes || [])
            clean = publishable(current)
            print = fingerprintOf(clean)
            writeNotes(dir, clean, ownRevision, "ardour", regionId)
            fingerprint = print
            statusMessage = "Applied Ardour revision " + ardour.revision + "."
            busy = false
            return
        }
        if (print !== fingerprint) {
            ownRevision = ownRevision + 1
            var region = ardour && ardour.region_id ? ardour.region_id : ""
            writeNotes(dir, clean, ownRevision, "mscore", region)
            fingerprint = print
            agentLog("E", "sent notes", { revision: ownRevision, count: clean.length, origin: "mscore", dir: dir })
            statusMessage = "Sent revision " + ownRevision + " to Ardour."
        }
    }
}
