# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

MCP_SERVER_URL = "https://tc-mcp-server.armin-908.workers.dev/mcp"

class MCPClient:
    """Client for communicating with the TravelClick MCP Server."""
    
    def __init__(self):
        self.session_id: Optional[str] = None
        self.request_id = 0
    
    def _get_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        return headers
    
    def _next_id(self) -> int:
        self.request_id += 1
        return self.request_id
    
    def _parse_sse_response(self, response_text: str) -> dict:
        """Parse Server-Sent Events response format."""
        for line in response_text.split('\n'):
            if line.startswith('data: '):
                return json.loads(line[6:])
        return {}
    
    def initialize(self) -> bool:
        """Initialize the MCP connection and get session ID."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "hotel-finder-agent",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            response = requests.post(
                MCP_SERVER_URL,
                json=request,
                headers=self._get_headers(),
                verify=True
            )
            
            # Extract session ID from headers
            self.session_id = response.headers.get("mcp-session-id")
            if self.session_id:
                logger.info(f"MCP session initialized: {self.session_id[:20]}...")
                return True
            else:
                logger.error("Failed to get MCP session ID")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize MCP connection: {e}")
            return False
    
    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call an MCP tool and return the result."""
        if not self.session_id:
            if not self.initialize():
                return {"error": "Failed to initialize MCP connection"}
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = requests.post(
                MCP_SERVER_URL,
                json=request,
                headers=self._get_headers(),
                verify=True
            )
            
            result = self._parse_sse_response(response.text)
            
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if content and len(content) > 0 and "text" in content[0]:
                    return json.loads(content[0]["text"])
            
            if "error" in result:
                return {"error": result["error"]}
                
            return result
            
        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            return {"error": str(e)}


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None

def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
        _mcp_client.initialize()
    return _mcp_client


def search_resorts(
    query: str = "",
    state: str = "",
    city: str = "",
    country: str = "",
    brand: str = "",
    limit: int = 5
) -> str:
    """Search for hotel resorts based on various criteria.
    
    Args:
        query: General search term - searches across name, city, state, and brand
        state: State/region to filter by (e.g., 'FL', 'Florida', 'California')
        city: City name to filter by
        country: Country to filter by (e.g., 'USA', 'Mexico')
        brand: Brand name to filter by (e.g., 'Wyndham', 'Margaritaville')
        limit: Maximum number of results to return (default: 5, max: 50)
    
    Returns:
        JSON string containing resort search results with names, addresses, amenities, etc.
    """
    logger.info(f"--- TOOL CALLED: search_resorts ---")
    logger.info(f"  - Query: {query}")
    logger.info(f"  - State: {state}, City: {city}, Country: {country}")
    logger.info(f"  - Brand: {brand}, Limit: {limit}")
    
    client = get_mcp_client()
    
    # Build arguments - at least one search param required
    arguments = {"limit": min(limit, 50)}
    if query:
        arguments["query"] = query
    if state:
        arguments["state"] = state
    if city:
        arguments["city"] = city
    if country:
        arguments["country"] = country
    if brand:
        arguments["brand"] = brand
    
    # Ensure at least one search parameter
    if len(arguments) == 1:  # Only limit
        arguments["country"] = "USA"  # Default to USA
    
    result = client.call_tool("search_resorts", arguments)
    
    if "error" in result:
        logger.error(f"  - Error: {result['error']}")
        return json.dumps({"error": result["error"]})
    
    logger.info(f"  - Success: Found {result.get('totalFound', 0)} resorts, returning {result.get('returned', 0)}")
    return json.dumps(result)


def get_resort_details(hotel_code: str) -> str:
    """Get detailed information about a specific resort.
    
    Args:
        hotel_code: The unique hotel/branch code for the resort
    
    Returns:
        JSON string containing resort details including description, address, 
        amenities, phone, URL, and image.
    """
    logger.info(f"--- TOOL CALLED: get_resort_details ---")
    logger.info(f"  - Hotel Code: {hotel_code}")
    
    client = get_mcp_client()
    result = client.call_tool("get_resort_details", {"hotelCode": hotel_code})
    
    if "error" in result:
        logger.error(f"  - Error: {result['error']}")
        return json.dumps({"error": result["error"]})
    
    logger.info(f"  - Success: Got details for {result.get('name', 'Unknown')}")
    return json.dumps(result)


def get_hotel_availability(
    hotel_code: str,
    date_in: str = "2026-02-01",
    date_out: str = "2026-02-05"
) -> str:
    """Get room availability and rates for a specific hotel.
    
    Args:
        hotel_code: The unique hotel/branch code for the resort
        date_in: Check-in date in YYYY-MM-DD format (default: 2026-02-01)
        date_out: Check-out date in YYYY-MM-DD format (default: 2026-02-05)
    
    Returns:
        JSON string containing available room types with rates, descriptions,
        amenities, bed types, and occupancy information.
    """
    logger.info(f"--- TOOL CALLED: get_hotel_availability ---")
    logger.info(f"  - Hotel Code: {hotel_code}")
    logger.info(f"  - Dates: {date_in} to {date_out}")
    
    client = get_mcp_client()
    result = client.call_tool("get_hotel_availability", {
        "hotelCode": hotel_code,
        "dateIn": date_in,
        "dateOut": date_out
    })
    
    if "error" in result or "errors" in result:
        error_msg = result.get("error") or result.get("errors", [{}])[0].get("errorMessage", "Unknown error")
        logger.error(f"  - Error: {error_msg}")
        return json.dumps({"error": error_msg, "hotelCode": hotel_code})
    
    room_count = len(result.get("roomStays", [{}])[0].get("roomTypes", []))
    logger.info(f"  - Success: Found {room_count} room types")
    return json.dumps(result)

