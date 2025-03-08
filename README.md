# Weather App

A command-line and MCP-based weather application that provides current weather conditions, forecasts, and alerts for locations worldwide.

## Features

- Get current weather conditions for any location
- Get daily weather forecasts
- Get hourly weather forecasts
- Get weather alerts
- Get weather by coordinates
- Automatic location detection
- Test API connection
- Check API key and subscription status

## Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone this repository:

   ```bash
   git clone <repository-url>
   cd weather-app
   ```

2. Create a `.env` file in the root directory with your OpenWeatherMap API key:

   ```bash
   OPENWEATHER_API_KEY=your_api_key_here
   ```

   You can get an API key from [OpenWeatherMap](https://openweathermap.org/api).

3. Run the installation script:

   ```bash
   ./scripts/install.sh
   ```

   For development setup, use:

   ```bash
   ./scripts/install.sh --dev
   ```

## Usage

Run the weather app:

```bash
./scripts/run_weather.sh
```

This will start the MCP server with the following available tools:

- `get_current_weather`: Get current weather conditions
- `get_forecast`: Get daily weather forecast
- `get_hourly_forecast`: Get hourly weather forecast
- `get_alerts`: Get weather alerts
- `get_weather_by_coordinates`: Get weather by coordinates
- `get_user_location`: Get your current location
- `test_api_connection`: Test the API connection
- `check_api_key_and_subscription`: Check your API key and subscription

## Development

### Code Style and Linting

This project uses:

- [Black](https://black.readthedocs.io/) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [Ruff](https://github.com/charliermarsh/ruff) for linting
- [mypy](https://mypy.readthedocs.io/) for type checking

All of these tools are configured in the `pyproject.toml` file.

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality. After installing the development dependencies, the hooks are automatically set up.

To manually install the pre-commit hooks:

```bash
uv run pre-commit install
```

To run the pre-commit hooks manually:

```bash
uv run pre-commit run --all-files
```

### Testing

Run the tests:

```bash
./scripts/run_tests.sh
```

Run with coverage:

```bash
./scripts/run_tests.sh --coverage
```

Run integration tests (requires API key):

```bash
./scripts/run_tests.sh --integration
```

Run integration tests with coverage:

```bash
./scripts/run_tests.sh --integration --coverage
```

## Creating an MCP Server

To create your own MCP server using this project as a template:

1. Install the project with development dependencies:

   ```bash
   ./scripts/install.sh --dev
   ```

2. Create a new Python file with your MCP server implementation:

   ```python
   import os
   from dotenv import load_dotenv
   from mcp.server.fastmcp import FastMCP

   # Load environment variables
   load_dotenv()

   # Initialize FastMCP server
   mcp = FastMCP("your-app-name")

   # Define your tools
   @mcp.tool
   async def your_tool(param1: str, param2: int) -> str:
       """Tool description."""
       # Your implementation here
       return "Result"

   # Run the server
   if __name__ == "__main__":
       mcp.run()
   ```

3. Run your server:

   ```bash
   python your_server.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
