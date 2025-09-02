#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -m nltk.downloader punkt -d /opt/render/nltk_data

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 10000
