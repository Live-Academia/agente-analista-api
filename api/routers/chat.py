"""Router: POST /api/chat e /api/chat/stream — Q&A sobre os dados."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.schemas import ChatRequest, ChatResponse
from api.security import get_current_user
from deep_agent.chains.qa import format_qa_data, qa_node
from deep_agent.config import get_llm
from deep_agent.prompts.qa_prompt import qa_prompt

router = APIRouter()


def _build_state_from_request(req: ChatRequest) -> dict:
    """Reconstroi o state minimo necessario para o qa_node a partir do JSON da API."""
    a = req.analysis_state
    return {
        "data_summary": a.get("data_summary", {}),
        "statistical_analysis": a.get("statistical_analysis", {}),
        "patterns": a.get("patterns", []),
        "insights": a.get("insights", []),
        "user_question": req.question,
        "mode": "qa",
        "raw_data": None,
        "file_path": None,
        "data_source": None,
        "error": None,
        "report": None,
        "qa_answer": None,
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    _user: dict = Depends(get_current_user),
) -> ChatResponse:
    """Responde uma pergunta sobre os dados (resposta completa)."""
    state = _build_state_from_request(req)
    result = qa_node(state)
    return ChatResponse(answer=result.get("qa_answer", "Sem resposta."))


@router.post("/chat/stream")
async def chat_stream(
    req: ChatRequest,
    _user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """Responde uma pergunta com streaming de tokens (SSE)."""
    import json

    state = _build_state_from_request(req)

    async def generate():
        try:
            llm = get_llm()
            chain = qa_prompt | llm
            prompt_data = format_qa_data(state)
            async for chunk in chain.astream(prompt_data):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            yield f"\n\n[Erro: {e}]"

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")
