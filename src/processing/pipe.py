import os
import shutil
from flask import current_app
from .chunk import chunk_extension
from .featuring import Prediction

class Pipe:    
    @staticmethod
    def create_folder(name):
        folder_path = os.path.join(current_app.config['UPLOAD_PATH'], name)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        os.mkdir(folder_path)
        return folder_path

    @staticmethod
    def get_filename_from_path(path):
        full_name = path.split("/")[-1]
        return full_name.split('.')[0]
    
    @staticmethod
    def process(path):
        filename = Pipe.get_filename_from_path(path)
        folder_path = Pipe.create_folder(filename)
        paths = chunk_extension.silence_cut_off(path, folder_path)
        transcript = Prediction.get_transcript(paths=paths)
        return transcript