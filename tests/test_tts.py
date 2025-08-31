import unittest
import os
import asyncio
from app.tts_generator import amain_multipart

class TestTTSGenerator(unittest.TestCase):

    def test_amain_multipart(self):
        # Define test parameters
        TEXT = "Hello world. This is a test."
        VOICE = "en-US-JennyNeural"
        OUTPUT_FILE = "test_output.mp3"

        # Run the async function
        asyncio.run(amain_multipart(TEXT, VOICE, OUTPUT_FILE))

        # Check if the output file was created
        self.assertTrue(os.path.exists(OUTPUT_FILE))

        # Clean up the output file
        os.remove(OUTPUT_FILE)

if __name__ == '__main__':
    unittest.main()