import glob
import pickle
from music21 import converter, instrument, note, chord

def get_notes():
    """
    Get all the notes and chords from the midi files in the ./maestro directory
    """
    notes = []

    for file in glob.glob("maestro/*.midi"):
        midi = converter.parse(file)

        print("Parsing %s" % file)

        for el in midi.flat.notes:
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
