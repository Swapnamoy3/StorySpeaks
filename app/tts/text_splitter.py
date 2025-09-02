import spacy
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.error("spaCy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'")
    raise

def split_text_into_chunks(text: str, max_sentences_per_chunk: int = 10) -> list[str]:
    if not text or not text.strip():
        logging.warning("Input text is empty or whitespace only.")
        return []

    try:
        # Process the text with spaCy
        doc = nlp(text.replace('\n', ' '))
        sentences = [sent.text.strip() for sent in doc.sents]

        if not sentences:
            logging.warning("spaCy sentence tokenization resulted in no sentences.")
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

    except Exception as e:
        logging.error(f"Error during text splitting: {e}")
        raise