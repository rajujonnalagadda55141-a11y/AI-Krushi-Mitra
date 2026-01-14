from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = OllamaEmbeddings(model="nomic-embed-text")

db = FAISS.load_local("backend/embeddings/faiss_index", embeddings, allow_dangerous_deserialization=True)

query = "My cotton leaves are yellow"
results = db.similarity_search(query, k=2)

for r in results:
    print("----")
    print(r.page_content)
