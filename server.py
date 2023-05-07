from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from flask import render_template

app = Flask(__name__)
preload_models()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/list", methods=["GET"])
def list_wav_files():
    files = [f for f in os.listdir('.') if f.endswith('.wav')]
    return jsonify(files)

@app.route("/delete/<string:filename>", methods=["DELETE"])
def delete_wav_file(filename):
    secure_name = secure_filename(filename)
    if os.path.exists(secure_name):
        os.remove(secure_name)
        return jsonify({"message": "File deleted."})
    else:
        return jsonify({"message": "File not found."}), 404

@app.route("/create", methods=["POST"])
def create_wav_file():
    data = request.json
    text_prompt = data.get("text_prompt", "")
    speaker = data.get("speaker")
    print(f"speaker: {speaker}")
    if speaker and speaker != "None":
        audio_array = generate_audio(text_prompt, history_prompt=speaker)
    else:
        audio_array = generate_audio(text_prompt)
    filename = f"{secure_filename(text_prompt[:10])}.wav"
    write_wav(filename, SAMPLE_RATE, audio_array)
    
    return jsonify({"message": "File created.", "filename": filename})

@app.route("/get/<string:filename>", methods=["GET"])
def get_wav_file(filename):
    secure_name = secure_filename(filename)
    if os.path.exists(secure_name):
        return send_file(secure_name)
    else:
        return jsonify({"message": "File not found."}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
