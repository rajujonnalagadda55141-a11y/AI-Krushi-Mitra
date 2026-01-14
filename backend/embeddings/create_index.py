from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import json
import os

# 1. Load all structured JSON data
DATA_DIR = "data/structured"

documents = []

for file in os.listdir(DATA_DIR):
    if file.endswith(".json"):
        with open(os.path.join(DATA_DIR, file), "r", encoding="utf-8") as f:
            items = json.load(f)
            for item in items:
                text = (
                    f"Crop: {item['crop']}. "
                    f"Issue: {item['issue']}. "
                    f"Cause: {item['cause']}. "
                    f"Solution: {item['solution']}."
                )
                documents.append(text)

print(f"Loaded {len(documents)} records")

# 2. Create embeddings using Ollama
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 3. Build FAISS index
vectorstore = FAISS.from_texts(documents, embeddings)

# 4. Save index
vectorstore.save_local("backend/embeddings/faiss_index")

print("✅ FAISS index created successfully")
