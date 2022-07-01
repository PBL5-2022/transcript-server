import os
import pathlib
import numpy as np
import tensorflow as tf

from keras import layers
from keras.models import load_model
import keras

commands_command = np.array(['đèn', 'quạt', 'bật', 'tắt'])
commands_id = np.array(['hai', 'một', 'ba'])

def auc(y_true, y_pred):
    auc = tf.metrics.auc(y_true, y_pred)[1]
    keras.backend.get_session().run(tf.local_variables_initializer())
    return auc

class Prediction:

    graph = tf.compat.v1.get_default_graph()
    saved_model = load_model(os.path.join(os.getcwd(), 'model/model-vietnamese.h5'),  custom_objects={'auc': auc})
    saved_number_model = load_model(os.path.join(os.getcwd(), 'model/MotHaiBaBon88.h5'),  custom_objects={'auc': auc});
    
    @staticmethod
    def decode_audio(audio_binary):
        audio, _ = tf.audio.decode_wav(audio_binary)
        return tf.squeeze(audio, axis=-1)

    @staticmethod
    def get_label(file_path):
        parts = tf.strings.split(file_path, os.path.sep)
        return parts[-2]

    @staticmethod
    def get_waveform_and_label(file_path):
        label = Prediction.get_label(file_path)
        audio_binary = tf.io.read_file(file_path)
        waveform = Prediction.decode_audio(audio_binary)
        return waveform, label

    @staticmethod
    def get_spectrogram(waveform):
        zero_padding = tf.zeros([16000] - tf.shape(waveform), dtype=tf.float32)
        waveform = tf.cast(waveform, tf.float32)
        equal_length = tf.concat([waveform, zero_padding], 0)
        spectrogram = tf.signal.stft(equal_length, frame_length=255, frame_step=128)
        spectrogram = tf.abs(spectrogram)
        return spectrogram

    @staticmethod
    def get_transcript(paths):
        transcript = []
        for index, path in enumerate(paths):
            audio_file = tf.io.read_file(path)
            waveform = Prediction.decode_audio(audio_file)
            spectrogram = Prediction.get_spectrogram(waveform)
            dims = tf.expand_dims(spectrogram, -1)
            audios = [dims.numpy()]
            audios = np.array(audios)
            if (index == 2):                
                temp = Prediction.saved_number_model.predict(audios)
                print('Temp: ', temp)
                predict = np.argmax(temp, axis=1)
                transcript.append(commands_id[predict[0]])

            temp = Prediction.saved_model.predict(audios)
            print('Temp: ', temp)
            predict = np.argmax(temp, axis=1)
            transcript.append(commands_command[predict[0]])
        return " ".join(transcript)
        # Concat result and return