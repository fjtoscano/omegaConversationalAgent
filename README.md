# Omega Conversational Agent

Agente conversacional inteligente basado en **Python**, **FastAPI**, **LangChain** y **LangGraph**, desplegado en modo **Platform Hosted** en **WSO2 Agent Manager (AMP)** y conectado al servidor **Omega Unified MCP Server** publicado a través de **WSO2 API Manager**.

---

## 🎯 Capacidades
El agente descubre y ejecuta dinámicamente las **29 herramientas** provistas por el servidor MCP unificado:
* **Gestión de Clientes/Usuarios**: consulta, búsqueda, creación, actualización y listado de pedidos/facturas de usuarios.
* **Catálogo de Productos**: búsqueda, filtrado por categorías/SKU, verificación de existencias y altas/actualizaciones.
* **Gestión de Pedidos**: altas de pedidos, seguimiento de estado, detalle de ítems comprados y cancelaciones.
* **Facturación**: consulta de facturas, vinculación con pedidos y clientes.

---

## ⚙️ Variables de Entorno
* `OPENAI_API_KEY`: Clave de API de OpenAI.
* `OPENAI_MODEL`: Modelo de lenguaje a utilizar (por defecto `gpt-4o-mini`).
* `OMEGA_MCP_URL`: URL del endpoint MCP (inyectada automáticamente por WSO2 Agent Manager al vincular `omega-mcp-server`).
* `OMEGA_MCP_API_KEY`: Clave de acceso al proxy MCP (si aplica).
* `USE_MCP`: `true` para activar el descubrimiento de herramientas MCP.
* `COMPANY_NAME`: Nombre corporativo en los prompts.
* `AGENT_VERSION`: Versión del agente (ej. `1.0.0`).

---

## 🚀 Despliegue en WSO2 Agent Manager (Platform Hosted)
1. Repositorio Git: `https://github.com/fjtoscano/omegaConversationalAgent`
2. Buildpack: Python 3.12 (`python main.py`)
3. Puerto HTTP: 8000
4. MCP Binding: `omega-mcp-server`
