from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel

from agent import build_agent, load_mcp_tools
from config import Config

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("omega-agent")

CONFIG = Config.from_env()

MCP_TOOLS: list[Any] = []
AGENT: Any = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global MCP_TOOLS, AGENT
    log.info("Iniciando Omega Conversational Agent (version=%s, company=%s)...", CONFIG.agent_version, CONFIG.company_name)
    try:
        MCP_TOOLS = await load_mcp_tools(CONFIG)
    except Exception as exc:
        log.warning("Fallo al inicializar herramientas MCP en el arranque: %s", exc)
        MCP_TOOLS = []

    AGENT = build_agent(CONFIG, MCP_TOOLS)
    log.info("Agente listo con %d herramientas MCP activas.", len(MCP_TOOLS))
    yield
    log.info("Deteniendo Omega Conversational Agent.")


app = FastAPI(title="Omega Conversational Agent", version="1.0.0", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    context: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str | None = None
    agent_version: str | None = None


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "agent": "omega-conversational-agent",
        "company": CONFIG.company_name,
        "agent_version": CONFIG.agent_version,
        "mcp_enabled": CONFIG.use_mcp,
        "mcp_tool_count": len(MCP_TOOLS),
        "mcp_url": CONFIG.mcp_url,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    global AGENT
    if AGENT is None:
        AGENT = build_agent(CONFIG, MCP_TOOLS)

    session_id = req.session_id or str(uuid.uuid4())

    try:
        result = await AGENT.ainvoke(
            {"messages": [HumanMessage(content=req.message)]},
            config={"configurable": {"thread_id": session_id}},
        )
    except Exception as exc:
        log.exception("Error al invocar el agente conversacional: %s", exc)
        raise HTTPException(status_code=500, detail=f"Error al procesar mensaje: {exc}") from exc

    final_content: Any = None
    for m in reversed(result.get("messages", [])):
        if isinstance(m, AIMessage):
            final_content = m.content
            break

    if final_content is None:
        final_content = "Disculpa, no pude generar una respuesta en este momento."

    if isinstance(final_content, list):
        final_content = "\n".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in final_content
        )

    return ChatResponse(
        response=str(final_content),
        session_id=session_id,
        agent_version=CONFIG.agent_version,
    )
