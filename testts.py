# import asyncio
# import random
# import time
# import edge_tts, os
# import tempfile
# from io import BytesIO
# import nltk

# def split_into_chunks(text: str):
#     sentence_cnt = 5
#     sentences = nltk.sent_tokenize(text.replace('\n', ' '))
#     sentences = [s.strip() for s in sentences if s.strip()]

#     sentence_cnt = max(sentence_cnt, int(len(sentences)/15))
    
    
#     chunks = []
#     for i in range(0, len(sentences),sentence_cnt):
#         chunks.append(' '.join(sentences[i: i + sentence_cnt]))
#     return chunks

# async def tts(text, voice = "en-US-JennyNeural", rate="+0%", volume="+0%", pitch="+0Hz"):
#     comm = edge_tts.Communicate(text = text, voice = voice, rate=rate, volume=volume, pitch=pitch)

#     buffer = BytesIO()
#     async for chunk in comm.stream():
#         if chunk["type"] == "audio":
#             audio_chunk = chunk.get("data", b'')
#             buffer.write(audio_chunk)
    
#     return buffer.getvalue()
    
    
    

    
    
# async def main():
#     with open("sample_text.txt", 'r', encoding='utf-8') as f: 
#         text = f.read().replace('\n', ' ')
    
#     chunks = split_into_chunks(text)
#     print([s[0: 10]  for s in chunks])
    
#     if os.path.exists("audio.mp3"):
#         os.remove("audio.mp3")
        
#     audios = await asyncio.gather(*(tts(chunk) for chunk in chunks))
#     for a in audios:
#         with open("audio.mp3",'ab') as f:
#             f.write(a)
    
# asyncio.run(main())
    
    
import os

name = os.getenv("My_name", "World")
hobby = os.getenv("hobby", "Sleeping")
print(f"hello {name} your hobby is {hobby}")