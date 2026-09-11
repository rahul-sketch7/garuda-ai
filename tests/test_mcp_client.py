import asyncio
import sys
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main():

    project_root = Path(__file__).resolve().parent.parent

    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "tools.mcp_server"],
        cwd=str(project_root)
    )

    client = Client(transport)

    async with client:

        print("MCP CONNECTION: OK")

        tools = await client.list_tools()

        print("\nAVAILABLE TOOLS:")

        for tool in tools:
            print("-", tool.name)

        result = await client.call_tool(
            "scam_intelligence",
            {
                "query": "bank account blocked OTP request"
            }
        )

        print("\nTOOL RESULT:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
    