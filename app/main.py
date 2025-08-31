from fastapi import FastAPI, Form, File, UploadFile, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import os
import logging

from .pdf_extractor import extract_text_from_pdf_bytes
from .tts.main_generator import amain_multipart

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static Directories ---
if not os.path.exists("generated_audio"):
    os.makedirs("generated_audio")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/audio", StaticFiles(directory="generated_audio"), name="audio")

# --- Pydantic Models ---
class VoiceTestRequest(BaseModel):
    text: str
    voice: str
    rate: str
    volume: str
    pitch: str

# --- Endpoints ---
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.post("/uploadPDF")
async def root(
    file: UploadFile = File(...),
    voice: str = Form(...),
    pitch: str = Form(...),
    rate: str = Form(...),
    volume: str = Form(...)
):
    logging.info(f"Received request to upload PDF: {file.filename}")
    logging.info(f"Voice settings: voice={voice}, pitch={pitch}, rate={rate}, volume={volume}")

    try:
        binary_contents = await file.read()
        logging.info("Successfully read PDF file from request.")

        text_contents = extract_text_from_pdf_bytes(binary_contents)
        logging.info(f"Extracted text from PDF (first 100 chars): {text_contents[:100]}")

        if not text_contents.strip():
            logging.warning("PDF contains no extractable text.")
            return JSONResponse(content={"error": "The provided PDF does not contain any text to read."}, status_code=400)

        filename = f"{uuid.uuid4()}.mp3"
        OUTPUT_FILE = os.path.join("generated_audio", filename)
        
        length = len(text_contents)
        sentences_per_chunk = 20
        
        logging.info("Starting TTS generation...")
        from .tts.main_generator import amain_multipart
        await amain_multipart(
            TEXT=text_contents, 
            VOICE=voice, 
            OUTPUT_FILE=OUTPUT_FILE, 
            rate=rate, 
            volume=volume, 
            pitch=pitch, 
            sentences_per_chunk=int(sentences_per_chunk)
        )
        logging.info(f"TTS generation successful. Output file: {OUTPUT_FILE}")

    except Exception as e:
        logging.error(f"An error occurred during PDF processing or TTS generation: {e}", exc_info=True)
        return JSONResponse(content={"error": "An internal server error occurred. Please check the logs for details."}, status_code=500)
    
    return {"link": f"/audio/{filename}"}

@app.post("/test-voice")
async def test_voice(request: VoiceTestRequest):
    filename = f"test_{uuid.uuid4()}.mp3"
    OUTPUT_FILE = os.path.join("generated_audio", filename)

    try:
        await amain_multipart(
            TEXT=request.text,
            VOICE=request.voice,
            OUTPUT_FILE=OUTPUT_FILE,
            rate=request.rate,
            volume=request.volume,
            pitch=request.pitch,
            sentences_per_chunk=1 # Short text, so one chunk is fine
        )
    except Exception as e:
        logging.error(f"Error during test voice generation: {e}", exc_info=True)
        return JSONResponse(content={"error": "Failed to generate test audio."}, status_code=500)

    return FileResponse(path=OUTPUT_FILE, filename=filename, media_type='audio/mpeg')