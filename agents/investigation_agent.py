import asyncio
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def investigate(
    message: str,
    fraud_type: str,
    signals: list[str]
) -> dict:

    project_root = Path(__file__).resolve().parent.parent

    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "tools.mcp_server"],
        cwd=str(project_root)
    )

    client = Client(transport)

    async with client:

        query = f"""
Message:
{message}

Fraud Type:
{fraud_type}

Detected Signals:
{", ".join(signals)}
"""

        result = await client.call_tool(
            "scam_intelligence",
            {
                "query": query
            }
        )

        return result.data