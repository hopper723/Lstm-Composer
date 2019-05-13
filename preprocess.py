import glob
import pickle
from music21 import converter, instrument, note, chord

def get_notes():
    """
    Get all the notes and chords from the midi files in the ./maestro directory
    """
    notes = []

    for file in glob.glob("midi_songs/*.mid"):
        midi = converter.parse(file)

        print("Parsing %s" % file)

        notes_to_parse = None

        try: # file has instrument parts
            s2 = instrument.partitionByInstrument(midi)
            notes_to_parse = s2.parts[0].recurse()
        except: # file has notes in a flat structure
            notes_to_parse = midi.flat.notes

        for el in notes_to_parse:
            if isinstance(el, note.Note):
                notes.append(str(el.pitch))
            elif isinstance(el, chord.Chord):
                """
                append every chord by encoding the id of every note in the
                chord together into a single string, with each note being
                separated by a dot
                """
                notes.append('.'.join(str(n) for n in el.normalOrder))

    with open('data/notes', 'wb') as filepath:
        pickle.dump(notes, filepath)

    return notes

if __name__ == "__main__":
    get_notes()
