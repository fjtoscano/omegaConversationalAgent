from __future__ import annotations

import logging
from typing import Any

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from config import Config

log = logging.getLogger("omega-agent")

SYSTEM_PROMPT_TEMPLATE = """Eres el asistente conversacional inteligente oficial de {company_name}.

Tu misión es atender a clientes y operadores facilitando la gestión comercial y operativa mediante las herramientas conectadas a la plataforma:
- Gestión de Usuarios y Clientes: listar usuarios, buscar por nombre o email, ver detalle de usuario, crear nuevos usuarios, actualizar datos y consultar sus pedidos o facturas asociadas.
- Catálogo de Productos: listar catálogo, buscar por nombre, categoría, sku o estado, consultar precios y existencias en almacén (stock), crear productos y modificar información.
- Gestión de Pedidos: crear pedidos para clientes, consultar estado y productos incluidos, buscar pedidos por estado o cliente, actualizar o cancelar pedidos.
- Facturación: consultar facturas de compras, buscar facturas por usuario o pedido, ver detalles e importes, emitir nuevas facturas vinculadas a pedidos existentes.

REGLAS DE CONDUCTA:
1. Responde SIEMPRE en español con tono profesional, amable, claro y estructurado.
2. Utiliza las herramientas del servidor MCP de Omega para consultar y operar con datos reales.
3. Presenta los datos de forma legible y organizada (listas, viñetas o resúmenes claros con precios, IDs y estados).
4. Cuando falten datos obligatorios para crear un registro (como nombre o email para un cliente, o usuario_id para un pedido), solicítalos con cortesía.
5. Confirma los resultados de cualquier operación de creación, actualización o eliminación indicando claramente los identificadores afectados.
"""


async def load_mcp_tools(cfg: Config) -> list[Any]:
    """Carga dinámicamente las herramientas desde el servidor MCP de Omega."""
    if not cfg.use_mcp or not cfg.mcp_url:
        log.warning("MCP está desactivado o mcp_url no está definida")
        return []

    log.info("Conectando al servidor MCP en: %s", cfg.mcp_url)

    from langchain_mcp_adapters.client import MultiServerMCPClient

    connection: dict[str, Any] = {
        "url": cfg.mcp_url,
        "transport": "streamable_http",
    }
    if cfg.mcp_api_key:
        connection["headers"] = {"X-API-Key": cfg.mcp_api_key}

    try:
        client = MultiServerMCPClient({"omega": connection})
        tools = await client.get_tools()
        log.info("Herramientas MCP descubiertas exitosamente (%d herramientas): %s", 
                 len(tools), [t.name for t in tools[:8]])
        return list(tools)
    except Exception as exc:
        log.error("No se pudieron cargar herramientas desde %s: %s", cfg.mcp_url, exc)
        return []


def build_agent(cfg: Config, mcp_tools: list[Any] | None = None) -> Any:
    """Construye el agente ReAct de LangGraph con memoria."""
    llm = ChatOpenAI(
        model=cfg.openai_model,
        temperature=0,
        api_key=cfg.openai_api_key or "sk-dummy",
    )

    tools = list(mcp_tools or [])
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        company_name=cfg.company_name,
    )

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )
