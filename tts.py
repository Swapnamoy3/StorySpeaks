#!/usr/bin/env python3

"""
Example to generate audio with preset voice using async/await.
Modified to support multi-part generation for long texts with improved robustness.
"""

import asyncio
import edge_tts
import os
import uuid
import nltk.downloader
from pydub import AudioSegment
import nltk
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download necessary NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
    logging.info("NLTK punkt tokenizer data found.")
except LookupError:
    logging.warning("NLTK punkt tokenizer data not found. Attempting to download...")
    try:
        nltk.download('punkt')
        logging.info("NLTK punkt tokenizer data downloaded successfully.")
    except Exception as e:
        logging.error(f"Failed to download NLTK punkt data: {e}")
        raise

# Helper function for robust text splitting
def split_text_into_chunks(text: str, max_sentences_per_chunk: int = 10) -> list[str]:
    """
    Splits text into chunks using NLTK sentence tokenization.
    Rejoins sentences up to max_sentences_per_chunk.
    """
    if not text or not text.strip():
        logging.warning("Input text is empty or whitespace only.")
        return []

    try:
        sentences = nltk.sent_tokenize(text.replace('\n', ' '))
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            logging.warning("NLTK sentence tokenization resulted in no sentences.")
            return []

        chunks = []
        current_chunk_sentences = []
        for i, sentence in enumerate(sentences):
            current_chunk_sentences.append(sentence)
            if len(current_chunk_sentences) >= max_sentences_per_chunk or i == len(sentences) - 1:
                if current_chunk_sentences:
                    chunks.append(" ".join(current_chunk_sentences))
                    current_chunk_sentences = []
        logging.info(f"Split text into {len(chunks)} chunks.")
        return chunks

    except LookupError:
        logging.error("NLTK punkt tokenizer data not found. Please ensure 'nltk.download('punkt')' ran successfully.")
        # raise
    except Exception as e:
        logging.error(f"Error during text splitting: {e}")
        raise

# Helper function for single chunk generation with Semaphore
async def generate_single_audio_chunk(
    semaphore: asyncio.Semaphore, TEXT: str, VOICE: str, OUTPUT_FILE: str,
    rate: str = "+0%", volume: str = "+0%", pitch: str = "+0Hz", retries: int = 3
) -> None:
    """
    Generates TTS audio for a single text chunk with retries and concurrency control.
    """
    async with semaphore:
        attempt = 0
        while attempt < retries:
            logging.info(f"Attempt {attempt + 1} for chunk: {OUTPUT_FILE}, Text: '{TEXT[:50]}...'")
            try:
                communicate = edge_tts.Communicate(TEXT, VOICE, rate=rate, volume=volume, pitch=pitch)
                await communicate.save(OUTPUT_FILE)
                logging.info(f"Audio chunk successfully saved to {OUTPUT_FILE}")
                return
            except Exception as e:
                attempt += 1
                logging.warning(f"Error during TTS generation for chunk {OUTPUT_FILE} (Attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logging.error(f"Failed to generate audio for chunk {OUTPUT_FILE} after {retries} attempts.")
                    raise RuntimeError(f"Failed to generate chunk {OUTPUT_FILE}") from e

# Main function to handle splitting, concurrent generation, and merging
async def amain_multipart(
    TEXT: str, VOICE: str, OUTPUT_FILE: str,
    rate: str = "+0%", volume: str = "+0%", pitch: str = "+0Hz",
    sentences_per_chunk: int = 5, max_concurrent_tasks: int = 5
) -> None:
    """
    Generates TTS audio from TEXT using the specified VOICE and parameters,
    saving it to OUTPUT_FILE. Splits long text for concurrent processing
    with improved robustness.
    """
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

        # Merge audio files
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
        # Cleanup temporary files
        logging.info("Cleaning up temporary files...")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError as e:
                    logging.warning(f"Error removing temporary file {temp_file}: {e}")

# Example of direct execution (not used when imported by FastAPI)
if __name__ == "__main__":
    async def test_run_multipart():
        sample_text_long = ""
        if not os.path.exists("sample_text.txt"):
            with open("sample_text.txt", "w") as f:
                f.write("This is the first sentence. This is the second sentence! And the third one? Yes, indeed. " * 50 +
                        "Mr. Smith went to London. Dr. Jones followed him. Their journey cost $3.14 per mile. E.g., they stopped at St. James's square.")
            logging.info("Created a dummy sample_text.txt for testing.")

        try:
            with open("sample_text.txt", "r", encoding='utf-8') as f:
                sample_text_long = f.read()
        except FileNotFoundError:
            logging.error("sample_text.txt not found.")
            return
        except Exception as e:
            logging.error(f"Error reading sample_text.txt: {e}")
            return

        logging.info(f"Read sample_text.txt, length: {len(sample_text_long)}")

        sample_voice = "en-US-JennyNeural"
        sample_output_multipart = "test_direct_run_multipart.mp3"
        sample_output_short = "test_direct_run_short_multipart.mp3"
        sample_text_short = "This is a short test sentence. It has two sentences."

        if os.path.exists(sample_output_multipart): os.remove(sample_output_multipart)
        if os.path.exists(sample_output_short): os.remove(sample_output_short)

        try:
            logging.info("\n--- Testing with LONG text ---")
            await amain_multipart(
                TEXT=sample_text_long,
                VOICE=sample_voice,
                OUTPUT_FILE=sample_output_multipart,
                sentences_per_chunk=10,
                max_concurrent_tasks=5
            )
            logging.info(f"Multipart Test TTS generated: {sample_output_multipart}")

            logging.info("\n--- Testing with SHORT text ---")
            await amain_multipart(
                TEXT=sample_text_short,
                VOICE=sample_voice,
                OUTPUT_FILE=sample_output_short,
                sentences_per_chunk=3,
                max_concurrent_tasks=2
            )
            logging.info(f"Multipart Test TTS (short) generated: {sample_output_short}")

            logging.info("\n--- Testing with EMPTY text ---")
            sample_output_empty = "test_direct_run_empty.mp3"
            if os.path.exists(sample_output_empty): os.remove(sample_output_empty)
            await amain_multipart(
                TEXT="",
                VOICE=sample_voice,
                OUTPUT_FILE=sample_output_empty,
                sentences_per_chunk=5,
                max_concurrent_tasks=2
            )
            logging.info(f"Empty text test completed. Output: {sample_output_empty}")
            if os.path.exists(sample_output_empty):
                logging.info(f"Empty output file size: {os.path.getsize(sample_output_empty)} bytes")

        except Exception as e:
            logging.error(f"Test run failed: {e}", exc_info=True)

    asyncio.run(test_run_multipart())