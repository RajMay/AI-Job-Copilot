import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import uuid

load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "resume-index")

# Initialize client
pc = Pinecone(api_key=API_KEY)

def store_resume_embeddings(chunks, embeddings, metadata=None):
    """
    Store resume chunks + vectors in Pinecone.
    """

    vectors = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        vector = {
            "id": str(uuid.uuid4()),
            "values": embedding,
            "metadata": {
                "text": chunk,
                **(metadata or {})
            }
        }

        vectors.append(vector)

    index.upsert(vectors)

def search_similar(query_embedding, top_k=5):

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    return results    


def get_or_create_index():

    if INDEX_NAME not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    return pc.Index(INDEX_NAME)


index = get_or_create_index()
