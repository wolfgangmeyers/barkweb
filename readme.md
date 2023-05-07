# Bark Audio Generator

Bark Audio Generator is a web application that generates audio files using the Bark library. It provides a simple UI to input a text prompt and select a speaker, and then generates a WAV file based on the input.

## Installation

Follow these steps to set up the Bark Audio Generator:

1. Make sure you have Python 3 installed. You can check your Python version by running:

```bash
python --version
```

2. Set up a virtual environment:

```bash
python -m venv venv
```

3. Activate the virtual environment:

* On Windows:

```bash
venv\Scripts\activate
```

* On macOS and Linux:

```bash
source venv/bin/activate
```

4. Install the required packages:

```bash
pip install git+https://github.com/suno-ai/bark.git && \
pip uninstall -y torch torchvision torchaudio && \
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu118
```

## Usage

1. Run the server:

```bash
python server.py
```

2. Open the web application in your browser at http://localhost:5000.
3. Use the UI to generate audio files based on text prompts and selected speakers.

## License

This project is licensed under the terms of the [Unlicense](https://unlicense.org/).
