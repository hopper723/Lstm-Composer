import glob
import pickle
import numpy
from music21 import converter, instrument, note, chord
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def get_notes():
    """
    Get all the notes and chords from the midi files in the ./maestro directory
    """
    notes = []

    with open('data/notes', 'rb') as filepath:
        notes = pickle.load(filepath)

    return notes

def prepare_data(notes, n_note):
    """ Prepare the sequences used by the Neural Network """
    timesteps = 100

    # get all pitch names
    note_names = sorted(set(n for n in notes))

     # create a dictionary to map pitches to integers
    note_to_int = dict((note, number) for number, note in enumerate(note_names))

    network_input = []
    network_output = []

    # create input sequences and the corresponding outputs
    for i in range(len(notes) - timesteps):
        note_sequence = notes[i:i + timesteps]
        next_note = notes[i + timesteps]
        network_input.append([note_to_int[note] for note in note_sequence])
        network_output.append(note_to_int[next_note])

    n_patterns = len(network_input)

    # reshape the input into a format compatible with LSTM layers
    network_input = numpy.reshape(network_input, (n_patterns, timesteps, 1))
    # normalize input
    network_input = network_input / float(n_note)
    # one-hot encode
    network_output = np_utils.to_categorical(network_output)

    return (network_input, network_output)

def setup_model(network_input, n_note):
    """ create the structure of the neural network """
    model = Sequential()

    """
    expected input data shape: (timesteps, 1)
    batch_size: None
    """
    model.add(LSTM(
        512,
        input_shape=(network_input.shape[1], network_input.shape[2]),
        return_sequences=True
    ))
    model.add(Dropout(0.3))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(512))
    model.add(Dense(256))
    model.add(Dropout(0.3))
    model.add(Dense(n_note))
    model.add(Activation('softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    return model

def train(model, network_input, network_output):
    """ train the neural network """
    filepath = "models/weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"
    checkpoint = ModelCheckpoint(
        filepath,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )
    callbacks_list = [checkpoint]

    model.fit(network_input, network_output, epochs=500, batch_size=64, callbacks=callbacks_list)

def train_model():
    """ Train a Neural Network to generate music """
    notes = get_notes()

    # get amount of pitch names
    n_note = len(set(notes))

    network_input, network_output = prepare_data(notes, n_note)

    model = setup_model(network_input, n_note)

    train(model, network_input, network_output)

if __name__ == "__main__":
    train_model()
