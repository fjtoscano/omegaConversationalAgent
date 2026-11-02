from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str | None = None) -> str:
    val = os.environ.get(name, default)
    if val is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return val


@dataclass(frozen=True)
class Config:
    company_name: str
    agent_version: str
    openai_api_key: str
    openai_model: str
    use_mcp: bool
    mcp_url: str
    mcp_api_key: str

    @classmethod
    def from_env(cls) -> "Config":
        company_name = _env("COMPANY_NAME", "Omega Enterprise Solutions")
        agent_version = _env("AGENT_VERSION", "1.0.0")
        openai_api_key = _env("OPENAI_API_KEY", "")
        openai_model = _env("OPENAI_MODEL", "gpt-4o-mini")

        use_mcp = _env("USE_MCP", "true").lower() in ("true", "1", "yes")

        # Injected by Agent Manager when omega-mcp is bound,
        # or defaults to APIM Gateway internal address
        mcp_url = _env("OMEGA_MCP_URL", "")
        if not mcp_url:
            mcp_url = _env("OMEGA_SERVICE_AGENT_MCP_CONFIG_URL", "")
        if not mcp_url:
            mcp_url = _env("MCP_SERVER_URL", "http://wso2-am-wso2am-all-in-one-am-service.wso2-dev.svc.cluster.local:8280/mcp/1.0.0/mcp")

        mcp_api_key = _env("OMEGA_MCP_API_KEY", "")
        if not mcp_api_key:
            mcp_api_key = _env("OMEGA_SERVICE_AGENT_MCP_CONFIG_API_KEY", "")

        return cls(
            company_name=company_name,
            agent_version=agent_version,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            use_mcp=use_mcp,
            mcp_url=mcp_url,
            mcp_api_key=mcp_api_key,
        )
