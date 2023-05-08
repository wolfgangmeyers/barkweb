from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from bark import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from flask import render_template
from bark.generation import load_codec_model, generate_text_semantic, CUR_PATH as BARK_PATH
from encodec.utils import convert_audio
import numpy as np
import torchaudio
import torch

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

@app.route("/upload", methods=["POST"])
def upload_wav_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file provided."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected."}), 400

    if file and file.filename.endswith(".wav"):
        secure_name = secure_filename(file.filename)
        file.save(os.path.join(".", secure_name))
        return jsonify({"message": "File uploaded.", "filename": secure_name})
    else:
        return jsonify({"message": "Invalid file type. Please upload a .wav file."}), 400

@app.route("/voices", methods=["GET"])
def list_voices():
    voices_path = os.path.join(BARK_PATH, "assets/prompts")
    voices = [f for f in os.listdir(voices_path) if f.endswith('.npz')]
    return jsonify(voices)

@app.route("/create_voice", methods=["POST"])
def create_voice():
    data = request.json
    audio_filepath = data.get("audio_sample")
    text = data.get("voice_text")
    voice_name = data.get("voice_name")
    print("data: ", data)

    model = load_codec_model(use_gpu=True)
    device = 'cuda'
    print("audio filepath: ", audio_filepath)
    wav, sr = torchaudio.load(audio_filepath)
    wav = convert_audio(wav, sr, model.sample_rate, model.channels)
    wav = wav.unsqueeze(0).to(device)
    
    with torch.no_grad():
        encoded_frames = model.encode(wav)
    codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()
    
    seconds = wav.shape[-1] / model.sample_rate
    semantic_tokens = generate_text_semantic(text, max_gen_duration_s=seconds, top_k=50, top_p=.95, temp=0.7)
    codes = codes.cpu().numpy()

    output_path = os.path.join(BARK_PATH, 'assets/prompts/' + voice_name + '.npz')
    # os.makedirs(os.path.dirname(output_path), exist_ok=True)
    np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)

    return jsonify({"message": "Voice created.", "filename": voice_name + '.npz'})

@app.route("/delete_voice/<string:filename>", methods=["DELETE"])
def delete_voice(filename):
    secure_name = secure_filename(filename)
    voice_path = os.path.join(BARK_PATH, "assets/prompts/", secure_name)

    if os.path.exists(voice_path):
        os.remove(voice_path)
        return jsonify({"message": "Voice deleted."})
    else:
        return jsonify({"message": "Voice not found."}), 404

if __name__ == "__main__":

    # one time move of files from cwd/bark/assets/prompts to $BARK_PATH/assets/prompts
    for f in os.listdir(os.path.join("bark", "assets", "prompts")):
        if f.endswith(".npz"):
            print(f"moving {f} to {BARK_PATH}")
            os.rename(os.path.join("bark", "assets", "prompts", f), os.path.join(BARK_PATH, "assets", "prompts", f))

    app.run(debug=True, host="0.0.0.0")
