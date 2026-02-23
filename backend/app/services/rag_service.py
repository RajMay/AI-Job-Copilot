from app.rag.embeddding import create_embeddings
from app.rag.pinecone_store import search_similar
from app.services.gemini_service import client  # Groq client
from typing import List


def retrieve_context(query: str, top_k: int = 5) -> List[str]:
    """
    Retrieve relevant resume chunks from Pinecone.
    """

    query_embedding = create_embeddings([query])[0]

    results = search_similar(query_embedding, top_k=top_k)

    contexts = [
        match["metadata"]["text"]
        for match in results["matches"]
    ]

    return contexts


def generate_rag_answer(query: str) -> str:
    """
    Generate answer using retrieved context + LLM.
    """

    contexts = retrieve_context(query)

    context_text = "\n\n".join(contexts)

    prompt = f"""
    You are an AI career assistant.

    Use ONLY the information below to answer.

    Context:
    {context_text}

    Question:
    {query}

    Answer clearly and concisely.
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content
