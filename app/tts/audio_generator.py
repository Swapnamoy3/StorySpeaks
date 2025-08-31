import asyncio
import edge_tts
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def generate_single_audio_chunk(
    semaphore: asyncio.Semaphore, TEXT: str, VOICE: str, OUTPUT_FILE: str,
    rate: str = "+0%", volume: str = "+0%", pitch: str = "+0Hz", retries: int = 3
) -> None:
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
