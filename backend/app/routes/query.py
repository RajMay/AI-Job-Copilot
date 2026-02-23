from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import generate_rag_answer

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
async def query_resume(data: QueryRequest):

    answer = generate_rag_answer(data.question)

    return {
        "question": data.question,
        "answer": answer
    }
