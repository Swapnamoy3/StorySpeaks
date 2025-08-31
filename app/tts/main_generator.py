import asyncio
import os
import uuid
import logging
from pydub import AudioSegment

from .text_splitter import split_text_into_chunks
from .audio_generator import generate_single_audio_chunk

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def amain_multipart(
    TEXT: str, VOICE: str, OUTPUT_FILE: str,
    rate: str = "+0%", volume: str = "+0%", pitch: str = "+0Hz",
    sentences_per_chunk: int = 5, max_concurrent_tasks: int = 5
) -> None:
    logging.info(f"Attempting to generate multi-part TTS: Voice={VOICE}, Rate={rate}, Volume={volume}, Pitch={pitch}")
    logging.info(f"Final output file: {OUTPUT_FILE}")
    logging.info(f"Splitting text with max_sentences_per_chunk={sentences_per_chunk}")

    text_chunks = split_text_into_chunks(TEXT, max_sentences_per_chunk=sentences_per_chunk)

    if not text_chunks:
        logging.warning("No text chunks to process after splitting. Creating empty output file.")
        try:
            AudioSegment.empty().export(OUTPUT_FILE, format="mp3")
            logging.info(f"Empty audio file created at {OUTPUT_FILE}")
        except Exception as e:
            logging.error(f"Failed to create empty output file {OUTPUT_FILE}: {e}")
            raise
        return

    output_dir = os.path.dirname(OUTPUT_FILE) or "."
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Created output directory: {output_dir}")

    temp_files = [os.path.join(output_dir, f"temp_audio_part_{i}_{uuid.uuid4()}.mp3") for i in range(len(text_chunks))]
    tasks = []
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    try:
        for i, chunk_text in enumerate(text_chunks):
            tasks.append(generate_single_audio_chunk(semaphore, chunk_text, VOICE, temp_files[i], rate, volume, pitch))

        logging.info(f"Starting generation of {len(tasks)} audio chunks with max {max_concurrent_tasks} concurrent tasks...")
        await asyncio.gather(*tasks)
        logging.info("All audio chunks generation tasks completed.")

        logging.info("Merging audio chunks...")
        combined_audio = AudioSegment.empty()
        for temp_file in temp_files:
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                try:
                    segment = AudioSegment.from_mp3(temp_file)
                    combined_audio += segment
                except Exception as e:
                    logging.warning(f"Error loading or appending audio segment {temp_file}: {e}. Skipping this chunk.")
            else:
                logging.warning(f"Temporary file {temp_file} is missing or empty. Skipping.")

        if not combined_audio:
            logging.error("No audio segments were successfully merged. Output file will not be created.")
            raise RuntimeError("Failed to merge any audio segments.")

        try:
            combined_audio.export(OUTPUT_FILE, format="mp3")
            logging.info(f"Merged TTS audio successfully saved to {OUTPUT_FILE}")
        except Exception as e:
            logging.error(f"Error exporting final audio file {OUTPUT_FILE}: {e}")
            raise

    except Exception as e:
        logging.error(f"Overall error during multi-part TTS generation: {e}")
        raise

    finally:
        logging.info("Cleaning up temporary files...")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError as e:
                    logging.warning(f"Error removing temporary file {temp_file}: {e}")
