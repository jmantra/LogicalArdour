#!/usr/bin/env python3

import mido
import numpy as np
from typing import List, Dict, Tuple
import random

class DrumLoopEditor:
    # MIDI note numbers for common drum hits
    DRUM_MAP = {
        'kick': 36,    # Bass Drum 1
        'snare': 38,   # Acoustic Snare
        'hihat': 42,   # Closed Hi-Hat
    }
    
    def __init__(self, midi_file: str):
        """Initialize the drum loop editor with a MIDI file."""
        self.midi_file = midi_file
        self.midi = mido.MidiFile(midi_file)
        self.ticks_per_beat = self.midi.ticks_per_beat
        self.tracks = self._extract_drum_tracks()
        self.loop_length = self._get_loop_length()
        
    def _get_loop_length(self) -> int:
        """Get the length of the loop in ticks."""
        max_time = 0
        for track in self.midi.tracks:
            current_time = 0
            for msg in track:
                current_time += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    max_time = max(max_time, current_time)
        return max_time
    
    def _extract_drum_tracks(self) -> Dict[str, List[Tuple[int, int, int]]]:
        """Extract drum hits from MIDI file and organize by drum type."""
        tracks = {drum: [] for drum in self.DRUM_MAP.keys()}
        
        current_time = 0
        for msg in self.midi.tracks[0]:
            current_time += msg.time
            
            if msg.type == 'note_on' and msg.velocity > 0:
                for drum_name, note in self.DRUM_MAP.items():
                    if msg.note == note:
                        tracks[drum_name].append((current_time, msg.note, msg.velocity))
        
        return tracks
    
    def _get_beat_positions(self) -> List[int]:
        """Get the positions of all beats in the loop."""
        beats = []
        for i in range(0, self.loop_length, self.ticks_per_beat):
            beats.append(i)
        return beats
    
    def _get_subdivision_positions(self, subdivision: int) -> List[int]:
        """Get positions for subdivisions of the beat."""
        positions = []
        for beat in self._get_beat_positions():
            for i in range(subdivision):
                pos = beat + (i * self.ticks_per_beat) // subdivision
                if pos < self.loop_length:
                    positions.append(pos)
        return positions
    
    def adjust_drum_quantity(self, drum_type: str, factor: float):
        """Adjust the quantity of a specific drum type.
        
        Args:
            drum_type: 'kick', 'snare', or 'hihat'
            factor: Multiplier for quantity (e.g., 1.5 for 50% more hits)
        """
        if drum_type not in self.DRUM_MAP:
            raise ValueError(f"Invalid drum type: {drum_type}")
            
        hits = self.tracks[drum_type]
        if not hits:
            return
            
        # Calculate how many hits to add
        target_count = int(len(hits) * factor)
        current_count = len(hits)
        
        if target_count > current_count:
            # Add more hits
            new_hits = []
            existing_positions = {time for time, _, _ in hits}
            
            # Get all possible positions (16th notes)
            all_positions = self._get_subdivision_positions(4)
            
            # Filter out positions that already have hits
            available_positions = [pos for pos in all_positions if pos not in existing_positions]
            
            # Add new hits at available positions
            num_to_add = target_count - current_count
            if available_positions:
                # Prioritize positions that are musically appropriate
                if drum_type == 'kick':
                    # Prefer positions on beats and off-beats
                    preferred_positions = [pos for pos in available_positions 
                                        if pos % self.ticks_per_beat < self.ticks_per_beat // 4]
                elif drum_type == 'snare':
                    # Prefer positions on beats 2 and 4
                    preferred_positions = [pos for pos in available_positions 
                                        if (pos // self.ticks_per_beat) % 2 == 1]
                else:  # hihat
                    # Prefer positions on 16th notes
                    preferred_positions = available_positions
                
                # Add hits at preferred positions first, then fall back to other positions
                positions_to_use = preferred_positions[:num_to_add]
                if len(positions_to_use) < num_to_add:
                    remaining = num_to_add - len(positions_to_use)
                    other_positions = [pos for pos in available_positions if pos not in positions_to_use]
                    positions_to_use.extend(random.sample(other_positions, min(remaining, len(other_positions))))
                
                for pos in positions_to_use:
                    # Use slightly lower velocity for added hits
                    velocity = random.randint(50, 90)
                    new_hits.append((pos, self.DRUM_MAP[drum_type], velocity))
            
            self.tracks[drum_type].extend(new_hits)
        
        # Sort hits by time
        self.tracks[drum_type].sort(key=lambda x: x[0])
    
    def adjust_velocity(self, drum_type: str, factor: float):
        """Adjust the velocity of a specific drum type.
        
        Args:
            drum_type: 'kick', 'snare', or 'hihat'
            factor: Multiplier for velocity (e.g., 1.2 for 20% louder)
        """
        if drum_type not in self.DRUM_MAP:
            raise ValueError(f"Invalid drum type: {drum_type}")
            
        for i, (time, note, velocity) in enumerate(self.tracks[drum_type]):
            new_velocity = min(127, int(velocity * factor))
            self.tracks[drum_type][i] = (time, note, new_velocity)
    
    def add_swing(self, amount: float):
        """Add swing to the groove.
        
        Args:
            amount: Swing amount (0.0 to 1.0, where 0.5 is maximum swing)
        """
        if not 0 <= amount <= 1:
            raise ValueError("Swing amount must be between 0 and 1")
            
        # Apply swing to all drum types
        for drum_type in self.DRUM_MAP.keys():
            for i, (time, note, velocity) in enumerate(self.tracks[drum_type]):
                # Calculate position within the beat
                beat_position = time % self.ticks_per_beat
                half_beat = self.ticks_per_beat // 2
                
                if beat_position < half_beat:  # First half of the beat
                    new_time = time + int(half_beat * amount)
                else:  # Second half of the beat
                    new_time = time - int(half_beat * amount)
                
                # Ensure the new time stays within the loop length
                new_time = new_time % self.loop_length
                self.tracks[drum_type][i] = (new_time, note, velocity)
    
    def save(self, output_file: str):
        """Save the modified drum loop to a new MIDI file."""
        new_midi = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = mido.MidiTrack()
        new_midi.tracks.append(track)
        
        # Copy tempo and time signature messages from original file
        for msg in self.midi.tracks[0]:
            if msg.type in ['set_tempo', 'time_signature']:
                track.append(msg)
        
        # Combine all drum hits
        all_hits = []
        for drum_hits in self.tracks.values():
            all_hits.extend(drum_hits)
        
        # Sort by time
        all_hits.sort(key=lambda x: x[0])
        
        # Convert to MIDI messages
        current_time = 0
        for time, note, velocity in all_hits:
            delta_time = int(time - current_time)
            track.append(mido.Message('note_on', note=note, velocity=velocity, time=delta_time))
            track.append(mido.Message('note_off', note=note, velocity=0, time=0))
            current_time = time
        
        # Add end of track message
        track.append(mido.MetaMessage('end_of_track', time=0))
        
        new_midi.save(output_file)

def main():
    # Example usage
    editor = DrumLoopEditor('input.mid')
    
    # Adjust quantities
    editor.adjust_drum_quantity('kick', 1.2)    # 20% more kicks
    editor.adjust_drum_quantity('snare', 0.8)   # 20% fewer snares
    editor.adjust_drum_quantity('hihat', 1.5)   # 50% more hi-hats
    
    # Adjust velocities
    editor.adjust_velocity('kick', 1.2)         # 20% louder kicks
    editor.adjust_velocity('snare', 0.9)        # 10% quieter snares
    
    # Add swing
    editor.add_swing(0.3)                       # Moderate swing
    
    # Save the result
    editor.save('output.mid')

if __name__ == '__main__':
    main() 