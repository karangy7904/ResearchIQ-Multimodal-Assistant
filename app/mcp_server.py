from mcp.server.fastmcp import FastMCP
from app.retrieval import retrieve_all

mcp = FastMCP("ResearchIQ-MCP")

@mcp.tool()
def search_research_papers(question: str) -> dict:
    """Search text, table and figure evidence in the ResearchIQ vector index."""
    return retrieve_all(question)

if __name__ == "__main__":
    # Run as a separate MCP stdio server for compatible external clients.
    mcp.run()
