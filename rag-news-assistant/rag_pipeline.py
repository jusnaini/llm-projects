from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from transformers import pipeline

class RAGPipeline:
    def __init__(self, docs, embedding_model="all-MiniLM-L6-v2", gen_model="google/flan-t5-base"):
        self.docs = docs
        self.embedder = SentenceTransformer(embedding_model)
        self.embeddings = self.embedder.encode(docs, convert_to_numpy=True)
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)
        self.generator = pipeline("text2text-generation", model=gen_model)

    def retrieve(self, query, top_k=3):
        query_emb = self.embedder.encode([query], convert_to_numpy=True)
        D, I = self.index.search(query_emb, top_k)
        return [self.docs[i] for i in I[0]]

    def generate(self, query, context):
        prompt = f"Context: {' '.join(context)}\n\nQuestion: {query}\nAnswer:"
        result = self.generator(prompt, max_new_tokens=64)
        return result[0]['generated_text']

    def answer(self, query):
        context = self.retrieve(query)
        return self.generate(query, context)