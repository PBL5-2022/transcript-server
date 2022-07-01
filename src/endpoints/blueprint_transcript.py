import os
from flask import Blueprint, jsonify, request, current_app, abort
from werkzeug.utils import secure_filename
from src.processing.pipe import Pipe

blueprint_transcript = Blueprint(name="blueprint_transcript", import_name=__name__)

DEVICES = {
    'quạt': 'fan',
    'đèn': 'led',
    'cửa': 'door',
}

IDENTIFY = {
    'một': 1,
    'hai': 2,
    'ba': 3,
    'bốn': 4,
}

keywords = ['một', 'hai', 'ba', 'bốn', 'bật', 'tắt', 'đèn', 'quạt', 'cửa']

def process_transcript(transcript):
    transcript = transcript.lower()
    arr = transcript.split(' ')
    if (len(arr) != 3):
        return None
    status = 'on' if arr[0] == 'bật' else 'off'
    device = DEVICES[arr[1]]
    id = IDENTIFY[arr[2]]
    
    if device == 'led':
        return {
            'status': status,
            'name': device + str(id),
            'path': '/' + device
        }
    elif device == 'fan':
        return {
            'value': 30 if status == 'on' else 0,
            'name': device + str(id),
            'path': '/' + device
        }
    elif device == 'door':
        return {
            'action': status,
            'path': '/' + device
        }

@blueprint_transcript.route('/', methods=['POST'], strict_slashes=False)
def post():
    uploaded_file = request.files['audio']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        file_path = os.path.join(current_app.config['UPLOAD_PATH'], filename)
        uploaded_file.save(file_path)
        transcript = Pipe.process(file_path)
        print(transcript)
        transcript = transcript.strip()
        for word in transcript.split(" "):
            if word not in keywords:
                return jsonify({ "data": None })
        # os.remove(file_path)
        return jsonify({ "data": process_transcript(transcript) })

    return jsonify({ "data": "Your transcript is processing" })
    


