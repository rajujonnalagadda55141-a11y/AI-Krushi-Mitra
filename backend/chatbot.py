from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama

# 1. Load embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 2. Load FAISS index
db = FAISS.load_local(
    "backend/embeddings/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

# 3. Load LLM
llm = Ollama(model="phi")

print("🌾 AI Krushi Mitra Chatbot")
print("Type 'exit' to quit\n")

while True:
    query = input("You: ")
    if query.lower() == "exit":
        break

    # 4. Search knowledge
    docs = db.similarity_search(query, k=3)

    # 5. Build context
    context = "\n".join([d.page_content for d in docs])

    # 6. Create prompt
    prompt = f"""
You are an agriculture expert.
Use the following knowledge to answer the farmer.

Knowledge:
{context}

Question:
{query}

Answer clearly in simple language.
"""

    # 7. Ask LLM
    response = llm.invoke(prompt)

    print("\n🤖 Bot:", response)
    print("-" * 50)
