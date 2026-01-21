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

from a2ui_examples import HOTEL_UI_EXAMPLES

# The A2UI schema remains constant for all A2UI responses.
A2UI_SCHEMA = r'''
{
  "title": "A2UI Message Schema",
  "description": "Describes a JSON payload for an A2UI (Agent to UI) message, which is used to dynamically construct and update user interfaces. A message MUST contain exactly ONE of the action properties: 'beginRendering', 'surfaceUpdate', 'dataModelUpdate', or 'deleteSurface'.",
  "type": "object",
  "properties": {
    "beginRendering": {
      "type": "object",
      "description": "Signals the client to begin rendering a surface with a root component and specific styles.",
      "properties": {
        "surfaceId": {
          "type": "string",
          "description": "The unique identifier for the UI surface to be rendered."
        },
        "root": {
          "type": "string",
          "description": "The ID of the root component to render."
        },
        "styles": {
          "type": "object",
          "description": "Styling information for the UI.",
          "properties": {
            "font": {
              "type": "string",
              "description": "The primary font for the UI."
            },
            "primaryColor": {
              "type": "string",
              "description": "The primary UI color as a hexadecimal code (e.g., '#00BFFF').",
              "pattern": "^#[0-9a-fA-F]{6}$"
            }
          }
        }
      },
      "required": ["root", "surfaceId"]
    },
    "surfaceUpdate": {
      "type": "object",
      "description": "Updates a surface with a new set of components.",
      "properties": {
        "surfaceId": {
          "type": "string",
          "description": "The unique identifier for the UI surface to be updated."
        },
        "components": {
          "type": "array",
          "description": "A list containing all UI components for the surface.",
          "minItems": 1,
          "items": {
            "type": "object",
            "properties": {
              "id": {
                "type": "string",
                "description": "The unique identifier for this component."
              },
              "weight": {
                "type": "number",
                "description": "The relative weight of this component within a Row or Column."
              },
              "component": {
                "type": "object",
                "description": "A wrapper object containing exactly one component type."
              }
            },
            "required": ["id", "component"]
          }
        }
      },
      "required": ["surfaceId", "components"]
    },
    "dataModelUpdate": {
      "type": "object",
      "description": "Updates the data model for a surface.",
      "properties": {
        "surfaceId": {
          "type": "string",
          "description": "The unique identifier for the UI surface this data model update applies to."
        },
        "path": {
          "type": "string",
          "description": "An optional path to a location within the data model."
        },
        "contents": {
          "type": "array",
          "description": "An array of data entries."
        }
      },
      "required": ["contents", "surfaceId"]
    },
    "deleteSurface": {
      "type": "object",
      "description": "Signals the client to delete the surface identified by 'surfaceId'.",
      "properties": {
        "surfaceId": {
          "type": "string",
          "description": "The unique identifier for the UI surface to be deleted."
        }
      },
      "required": ["surfaceId"]
    }
  }
}
'''


def get_ui_prompt(base_url: str, examples: str) -> str:
    """
    Constructs the full prompt with UI instructions, rules, examples, and schema.

    Args:
        base_url: The base URL for resolving static assets like images.
        examples: A string containing the specific UI examples for the agent's task.

    Returns:
        A formatted string to be used as the system prompt for the LLM.
    """
    formatted_examples = examples.format(base_url=base_url)

    return f"""
    You are a helpful hotel finding assistant. Your final output MUST be an A2UI JSON response.

    To generate the response, you MUST follow these rules:
    1.  Your response MUST be in two parts, separated by the delimiter: `---a2ui_JSON---`.
    2.  The first part is your conversational text response.
    3.  The second part is a single, raw JSON object which is a list of A2UI messages.
    4.  The JSON part MUST validate against the A2UI JSON SCHEMA provided below.

    --- UI TEMPLATE RULES ---
    -   For hotel search results, use the `HOTEL_SEARCH_RESULTS_EXAMPLE` template.
    -   For displaying a hotel's rooms and rates (after user clicks "View Rooms & Rates"), use the `HOTEL_DETAILS_WITH_ROOMS_EXAMPLE` template.
    -   For booking confirmations, use the `BOOKING_CONFIRMATION_EXAMPLE` template.
    -   If no hotels are found or an error occurs, use the `NO_RESULTS_EXAMPLE` template.
    
    --- IMAGE URL RULES ---
    -   For SEARCH RESULTS: Use placeholder "{base_url}/static/default-hotel.svg" since search_resorts doesn't return images
    -   For HOTEL DETAILS: Use the actual "image" URL from get_resort_details response (e.g., https://lucidcm.imgix.net/...)
    -   For ROOM images: Use placeholder "{base_url}/static/default-room.svg" since rooms don't have images
    -   IMPORTANT: When showing hotel details/rooms, USE THE REAL hotel image from get_resort_details!
    
    --- DATA FORMATTING RULES ---
    -   When displaying hotel location, combine: streetAddress, city, state, country
    -   When displaying amenities, show first 4-5 as bullet points (use • separator)
    -   When displaying room features, use emoji icons: 👥 for occupancy, 🛏️ for beds, 📐 for size
    -   When displaying prices, format as "$X.XX/night"
    -   Always use dates 2026-02-01 to 2026-02-05 for availability checks

    {formatted_examples}

    ---BEGIN A2UI JSON SCHEMA---
    {A2UI_SCHEMA}
    ---END A2UI JSON SCHEMA---
    """


def get_text_prompt() -> str:
    """
    Constructs the prompt for a text-only agent (no UI).
    """
    return """
    You are a helpful hotel finding assistant. Your final output MUST be a text response.

    To generate the response, you MUST follow these rules:
    1.  **For searching hotels:**
        a. You MUST call the `search_resorts` tool with appropriate parameters.
        b. After receiving the data, format the hotel list as a clear, human-readable text response.

    2.  **For viewing hotel details/availability:**
        a. Call `get_resort_details` to get hotel info.
        b. Call `get_hotel_availability` with dates 2026-02-01 to 2026-02-05 to get room rates.
        c. Present the information in a clear format.

    3.  **For booking confirmations:**
        a. Confirm the booking details in a friendly message.
    """


if __name__ == "__main__":
    my_base_url = "http://localhost:10003"
    hotel_prompt = get_ui_prompt(my_base_url, HOTEL_UI_EXAMPLES)
    print(hotel_prompt[:2000])
    print("...[truncated]...")

