"""Entry point for the weather app."""

from weather.weather import mcp

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
