import chromadb
from google import genai

class RagEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.ai_client = genai.Client()

    def add_documents(self, chunks: list[str], collection_name: str):
        collection = self.client.get_or_create_collection(name=collection_name)
        ids = []
        embeddings = []
        documents = []
        for i, chunk in enumerate(chunks):
            ids.append(f"chunk_{i}")
            response = self.ai_client.models.embed_content(
                model="text-embedding-004",
                contents=chunk
            )
            embeddings.append(response.embeddings[0].values)
            documents.append(chunk)
        collection.add(ids=ids, embeddings=embeddings, documents=documents)

    def search(self, query: str, collection_name: str) -> list[str]:
        collection = self.client.get_or_create_collection(name=collection_name)
        response = self.ai_client.models.embed_content(
            model="text-embedding-004",
            contents=query
        )
        query_embedding = response.embeddings[0].values
        results = collection.query(
            query_embeddings=[query_embedding]
        )
        return results["documents"][0]

    def answer_question(self, query: str, collection_name: str) -> str:
        context = self.search(query, collection_name)
        prompt = f"""
        Answer the question based only on this context:
        Context:{context}
        Question:{query}
        """
        response = self.ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
