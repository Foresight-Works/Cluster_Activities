Running
transformer_model = SentenceTransformer(sentences_model)
sometimes gets:
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='huggingface.co', port=443): Max retries exceeded with url: /api/models/sentence-transformers/all-MiniLM-L6-v2 (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f613b5d4070>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution'))

Download and load SentenceTransformers models locally
https://stackoverflow.com/questions/65419499/download-pre-trained-sentence-transformers-model-locally
Check download/load for gensim models as well
Repeat the necessary steps on the rnd