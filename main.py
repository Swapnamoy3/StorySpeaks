from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os

from pdfExtractor import extract_text_from_pdf_bytes
from tts import amain_multipart

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/uploadPDF")
async def root(
    file: UploadFile = File(...),
    voice: str = Form(...),
    pitch: str = Form(...),
    rate: str = Form(...),
    volume: str = Form(...)
):

    binary_contents = await file.read()
    text_contents = extract_text_from_pdf_bytes(binary_contents)
    OUTPUT_FILE = f"{uuid.uuid4()}.mp3"    
    
    try:
        
        length = len(text_contents)
        parts = 20
        cps = 120
        sentences_per_chunk = length // (parts * cps)
        
        await amain_multipart(TEXT=text_contents, VOICE=voice, OUTPUT_FILE=OUTPUT_FILE, rate=rate, volume=volume, pitch=pitch, sentences_per_chunk = int(max(10, sentences_per_chunk)))
    except Exception as e:
        print(f"Error during TTS generation: {e}")
    
    print(f"Text extracted from PDF: {text_contents[:100]}")
    
    print(f"Pitch: {pitch}, Rate: {rate}, Volume: {volume}")
    
    return {"message": "Hello World", "link": "http://127.0.0.1:8000/fileDownload/" + OUTPUT_FILE}



@app.get("/fileDownload/{filename}")
async def download_file(filename: str):
    file_path = filename
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )