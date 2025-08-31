# StorySpeaks

## Overview
StorySpeaks is a web application that allows users to convert PDF storybooks into narrated audio files. Leveraging Edge's neural text-to-speech (TTS) AI, it provides a seamless experience for transforming written content into engaging audio, with customizable voice, pitch, rate, and volume settings.

## Features
- **PDF to Audio Conversion:** Upload any PDF document and convert its text content into an audio file.
- **Customizable Voice:** Choose from a wide range of neural voices provided by Edge's TTS engine.
- **Adjustable Audio Settings:** Fine-tune the narration with controls for pitch, speaking rate, and volume.
- **Real-time Feedback:** Get status updates during the conversion process, including file upload, text extraction, and audio generation.
- **Direct Download & Playback:** Automatically download the generated audio file and play it directly within the browser.
- **Clean and Responsive UI:** A modern, user-friendly interface built with Tailwind CSS.

## Technologies Used
- **Backend:**
    - FastAPI: A modern, fast (high-performance) web framework for building APIs with Python 3.7+.
    - `pypdf`: For robust PDF text extraction.
    - `edge-tts`: Python library for interacting with Microsoft Edge's online text-to-speech service.
    - `pydub`: For audio manipulation and merging of generated audio chunks.
    - `nltk`: For natural language processing, specifically sentence tokenization.
- **Frontend:**
    - HTML5
    - Tailwind CSS: A utility-first CSS framework for rapidly building custom designs.
    - JavaScript: For interactive elements and API communication.

## Setup and Installation
To get StorySpeaks up and running on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Swapnamoy3/StorySpeaks.git
    cd StorySpeaks
    ```

2.  **Create and activate a virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run
Once the dependencies are installed, you can start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

- The `--reload` flag enables auto-reloading of the server on code changes, which is useful during development.
- The application will typically run on `http://127.0.0.1:8000`.

## Project Structure
```
StorySpeaks/
├── app/
│   ├── __init__.py
│   ├── main.py             # Main FastAPI application
│   ├── pdf_extractor.py    # PDF text extraction logic
│   └── tts/                # Text-to-Speech modules
│       ├── __init__.py
│       ├── audio_generator.py # Generates single audio chunks
│       ├── main_generator.py  # Orchestrates multi-part TTS generation
│       └── text_splitter.py   # Splits text into sentences/chunks
├── static/                 # Frontend assets (HTML, CSS, JS)
│   ├── index.html
│   └── script.js
├── tests/                  # Unit tests
│   ├── __init__.py
│   └── test_tts.py
├── generated_audio/        # Directory for generated audio files (ignored by Git)
├── _archive/               # Contains old, irrelevant files moved during refactoring
├── .gitignore              # Git ignore rules
├── README.md               # Project README file
├── requirements.txt        # Python dependencies
└── voices.txt              # List of available Edge TTS voices
```

## Usage
1.  **Access the Application:** Open your web browser and navigate to `http://127.0.0.1:8000`.
2.  **Upload PDF:** Click on "Select PDF File" and choose a PDF document from your computer.
3.  **Customize Voice:** Select your preferred voice and adjust pitch, rate, and volume using the sliders.
4.  **Generate Audio:** Click the "Generate & Download" button. The application will process the PDF, convert the text to speech, and automatically download the audio file. You can also play the audio directly in the browser.

## Contributing
Contributions are welcome! If you have suggestions for improvements or find any bugs, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details. (Note: A LICENSE file is not yet present in the repository, but this is a placeholder for future inclusion.)