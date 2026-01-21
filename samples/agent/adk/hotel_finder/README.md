# Hotel Finder Agent

An A2UI-powered agent that helps users find hotel resorts, view room availability and rates, and make bookings. This agent connects to a TravelClick MCP server to fetch real hotel data.

## Features

- **Search Hotels**: Find hotels by location (state, city), brand, or general query
- **View Details**: See hotel descriptions, amenities, and contact information
- **Room Availability**: Check available room types with pricing for specific dates
- **Book Rooms**: Confirm room reservations

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- A Gemini API key (get one free from [Google AI Studio](https://aistudio.google.com/apikey))

## Setup

1. **Set your Gemini API key:**

   ```bash
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```

2. **Navigate to the agent directory:**

   ```bash
   cd samples/agent/adk/hotel_finder
   ```

3. **Run the agent:**

   ```bash
   uv run .
   ```

   The agent will start on `http://localhost:10003` by default.

## MCP Server Integration

This agent connects to the TravelClick MCP Server at:
- URL: `https://tc-mcp-server.armin-908.workers.dev/mcp`

Available MCP tools:
- `search_resorts`: Search for hotels by location, brand, etc.
- `get_resort_details`: Get detailed information about a specific hotel
- `get_hotel_availability`: Check room availability and rates

## Running with the Angular Client

1. Start the agent (see above)

2. In a new terminal, start the Angular client:

   ```bash
   cd samples/client/angular
   npm install
   npm run start:hotel
   ```

3. Open `http://localhost:4001` in your browser

## Example Queries

- "Find hotels in Florida"
- "Search for Wyndham resorts in New Orleans"
- "Show me hotels in Texas"

## Configuration

- **Port**: Default is `10003`. Change with `--port` flag:
  ```bash
  uv run . --port 10004
  ```

- **Host**: Default is `localhost`. Change with `--host` flag:
  ```bash
  uv run . --host 0.0.0.0
  ```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Angular Client │────▶│  Hotel Agent     │────▶│  Gemini 2.5     │
│  (A2UI Renderer)│     │  (A2A Server)    │     │  Flash          │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  TravelClick     │
                        │  MCP Server      │
                        └──────────────────┘
```

## License

Apache 2.0 - See LICENSE file in the repository root.

