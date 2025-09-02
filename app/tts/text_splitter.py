import nltk

import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download necessary NLTK data if not already present
def download_NLTK():
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

download_NLTK()

def split_text_into_chunks(text: str, max_sentences_per_chunk: int = 10) -> list[str]:
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
        raise
    except Exception as e:
        logging.error(f"Error during text splitting: {e}")
        raise
