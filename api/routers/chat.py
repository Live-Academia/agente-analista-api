"""Router: POST /api/chat e /api/chat/stream — Q&A sobre os dados."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.schemas import ChatRequest, ChatResponse
from api.security import get_current_user
from deep_agent.chains.qa import format_qa_data, qa_node
from deep_agent.config import get_llm
from deep_agent.prompts.qa_prompt import qa_prompt
from deep_agent.storage.history import save_message
from deep_agent.storage.logger import log_operation

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
        "template": a.get("template_used"),
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
    username = _user.get("username", "")
    session_id = req.session_id
    source_name = req.analysis_state.get("source_name", "")

    result = qa_node(state)
    answer = result.get("qa_answer", "Sem resposta.")

    if session_id:
        save_message(session_id, username, "user", req.question)
        save_message(session_id, username, "assistant", answer)

    log_operation("chat", status="ok", session_id=session_id, username=username,
                  source_name=source_name)

    return ChatResponse(answer=answer)


@router.post("/chat/stream")
async def chat_stream(
    req: ChatRequest,
    _user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """Responde uma pergunta com streaming de tokens (SSE)."""
    state = _build_state_from_request(req)
    username = _user.get("username", "")
    session_id = req.session_id
    source_name = req.analysis_state.get("source_name", "")

    if session_id:
        save_message(session_id, username, "user", req.question)

    async def generate():
        full_answer: list[str] = []
        try:
            llm = get_llm()
            chain = qa_prompt | llm
            prompt_data = format_qa_data(state)
            async for chunk in chain.astream(prompt_data):
                if chunk.content:
                    full_answer.append(chunk.content)
                    yield chunk.content
        except Exception as e:
            yield f"\n\n[Erro: {e}]"
        finally:
            if session_id and full_answer:
                save_message(session_id, username, "assistant", "".join(full_answer))
            log_operation("chat_stream", status="ok", session_id=session_id,
                          username=username, source_name=source_name)

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")
