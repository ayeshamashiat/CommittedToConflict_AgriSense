"""POST /retrieve - RAG search over the agronomy knowledge base (ChromaDB)."""

import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db
from app.db.repositories.session_repo import get_or_create_session
from app.db.repositories.tool_log_repo import log_tool_call
from app.schemas.tool_io import RAGInput, RAGOutput
from app.tools.rag_tool import RAGTool

router = APIRouter(tags=["retrieve"])
_tool = RAGTool()


class RetrieveRequest(RAGInput):
    session_id: str | None = None


class RetrieveResponse(RAGOutput):
    session_id: str


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(payload: RetrieveRequest, db: DBSession = Depends(get_db)) -> RetrieveResponse:
    session = get_or_create_session(db, payload.session_id)
    input_data = RAGInput(query=payload.query, n_results=payload.n_results)

    started = time.perf_counter()
    result = _tool.run(input_data)

    log_tool_call(
        db,
        session_id=session.id,
        tool_name=_tool.name,
        input_json=input_data.model_dump(),
        output_json=result.model_dump(),
        status="success",
        latency_ms=(time.perf_counter() - started) * 1000,
    )

    return RetrieveResponse(session_id=session.id, **result.model_dump())
