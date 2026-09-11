from fastmcp import FastMCP

from tools.scam_intelligence import search_scam_intelligence


mcp = FastMCP("FraudShield")


@mcp.tool
def scam_intelligence(query: str) -> dict:
    """
    Search FraudShield's trusted scam intelligence knowledge base.
    """

    return search_scam_intelligence(query)


if __name__ == "__main__":
    mcp.run()