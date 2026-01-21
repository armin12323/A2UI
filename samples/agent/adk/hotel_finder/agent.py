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
import os
from collections.abc import AsyncIterable
from typing import Any

import jsonschema
import litellm
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from prompt_builder import (
    A2UI_SCHEMA,
    HOTEL_UI_EXAMPLES,
    get_text_prompt,
    get_ui_prompt,
)
from tools import search_resorts, get_resort_details, get_hotel_availability

logger = logging.getLogger(__name__)

AGENT_INSTRUCTION = """
    You are a helpful hotel finding assistant. Your goal is to help users find and book hotel rooms using a rich UI.

    To achieve this, you MUST follow this logic:

    1.  **For searching hotels:**
        a. You MUST call the `search_resorts` tool with the user's criteria (state, city, brand, etc.).
        b. After receiving the data, generate the UI JSON using the HOTEL_SEARCH_RESULTS_EXAMPLE template.
        c. Populate the dataModelUpdate with hotel data from the tool response.
        d. ALWAYS use the default image URL for all hotels: {base_url}/static/default-hotel.png

    2.  **For viewing hotel details/rooms (when you receive 'view_hotel_details' action):**
        a. Extract the hotelCode from the action context.
        b. Call `get_resort_details` to get the hotel's full information.
        c. Call `get_hotel_availability` with hotelCode and dates 2026-02-01 to 2026-02-05.
        d. Generate UI using the HOTEL_DETAILS_WITH_ROOMS_EXAMPLE template.
        e. Populate with hotel info and available room types with their rates.
        f. ALWAYS use the default image URL for all images: {base_url}/static/default-hotel.png

    3.  **For booking a room (when you receive 'book_room' action):**
        a. Extract booking details from the action context.
        b. Generate a booking confirmation using the BOOKING_CONFIRMATION_EXAMPLE template.
        c. Calculate total price (nightly rate × 4 nights).
"""


class HotelAgent:
    """An agent that finds hotels and displays room availability using A2UI."""

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"] 

    def __init__(self, base_url: str, use_ui: bool = False):
        self.base_url = base_url
        self.use_ui = use_ui
        self._agent = self._build_agent(use_ui)
        self._user_id = "remote_agent"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        # Load the A2UI schema for validation
        try:
            single_message_schema = json.loads(A2UI_SCHEMA)
            self.a2ui_schema_object = {"type": "array", "items": single_message_schema}
            logger.info("A2UI_SCHEMA successfully loaded and wrapped in an array validator.")
        except json.JSONDecodeError as e:
            logger.error(f"CRITICAL: Failed to parse A2UI_SCHEMA: {e}")
            self.a2ui_schema_object = None

    def get_processing_message(self) -> str:
        return "Searching for the best hotels for you..."

    def _build_agent(self, use_ui: bool) -> LlmAgent:
        """Builds the LLM agent for the hotel agent."""
        # Use Gemini 2.5 Flash Lite
        LITELLM_MODEL = os.getenv("LITELLM_MODEL", "gemini/gemini-2.5-flash")

        if use_ui:
            instruction = AGENT_INSTRUCTION.format(base_url=self.base_url) + get_ui_prompt(
                self.base_url, HOTEL_UI_EXAMPLES
            )
        else:
            instruction = get_text_prompt()

        return LlmAgent(
            model=LiteLlm(model=LITELLM_MODEL),
            name="hotel_agent",
            description="An agent that finds hotels and helps book rooms.",
            instruction=instruction,
            tools=[search_resorts, get_resort_details, get_hotel_availability],
        )

    async def stream(self, query, session_id) -> AsyncIterable[dict[str, Any]]:
        session_state = {"base_url": self.base_url}

        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state=session_state,
                session_id=session_id,
            )
        elif "base_url" not in session.state:
            session.state["base_url"] = self.base_url

        # UI Validation and Retry Logic
        max_retries = 1
        attempt = 0
        current_query_text = query

        if self.use_ui and self.a2ui_schema_object is None:
            logger.error("A2UI_SCHEMA is not loaded. Cannot perform UI validation.")
            yield {
                "is_task_complete": True,
                "content": "I'm sorry, I'm facing an internal configuration error. Please contact support.",
            }
            return

        while attempt <= max_retries:
            attempt += 1
            logger.info(f"--- HotelAgent.stream: Attempt {attempt}/{max_retries + 1} for session {session_id} ---")

            current_message = types.Content(
                role="user", parts=[types.Part.from_text(text=current_query_text)]
            )
            final_response_content = None

            async for event in self._runner.run_async(
                user_id=self._user_id,
                session_id=session.id,
                new_message=current_message,
            ):
                logger.info(f"Event from runner: {event}")
                if event.is_final_response():
                    if event.content and event.content.parts and event.content.parts[0].text:
                        final_response_content = "\n".join(
                            [p.text for p in event.content.parts if p.text]
                        )
                    break
                else:
                    logger.info(f"Intermediate event: {event}")
                    yield {
                        "is_task_complete": False,
                        "updates": self.get_processing_message(),
                    }

            if final_response_content is None:
                logger.warning(f"Received no final response content (Attempt {attempt}).")
                if attempt <= max_retries:
                    current_query_text = f"I received no response. Please retry: '{query}'"
                    continue
                else:
                    final_response_content = "I'm sorry, I encountered an error and couldn't process your request."

            is_valid = False
            error_message = ""

            if self.use_ui:
                logger.info(f"Validating UI response (Attempt {attempt})...")
                try:
                    if "---a2ui_JSON---" not in final_response_content:
                        raise ValueError("Delimiter '---a2ui_JSON---' not found.")

                    text_part, json_string = final_response_content.split("---a2ui_JSON---", 1)

                    if not json_string.strip():
                        raise ValueError("JSON part is empty.")

                    json_string_cleaned = json_string.strip().lstrip("```json").rstrip("```").strip()

                    if not json_string_cleaned:
                        raise ValueError("Cleaned JSON string is empty.")

                    parsed_json_data = json.loads(json_string_cleaned)
                    jsonschema.validate(instance=parsed_json_data, schema=self.a2ui_schema_object)

                    logger.info(f"UI JSON successfully validated (Attempt {attempt}).")
                    is_valid = True

                except (ValueError, json.JSONDecodeError, jsonschema.exceptions.ValidationError) as e:
                    logger.warning(f"A2UI validation failed: {e} (Attempt {attempt})")
                    logger.warning(f"Failed response content: {final_response_content[:500]}...")
                    error_message = f"Validation failed: {e}."
            else:
                is_valid = True

            if is_valid:
                logger.info(f"Response is valid. Sending final response (Attempt {attempt}).")
                
                # Log token usage
                try:
                    from litellm import token_counter
                    # Estimate tokens (LiteLLM provides this utility)
                    prompt_tokens = token_counter(model="gemini/gemini-2.5-flash", text=current_query_text)
                    response_tokens = token_counter(model="gemini/gemini-2.5-flash", text=final_response_content or "")
                    total_tokens = prompt_tokens + response_tokens
                    
                    print("\n" + "="*50)
                    print("📊 TOKEN USAGE")
                    print("="*50)
                    print(f"  Input tokens:  ~{prompt_tokens:,}")
                    print(f"  Output tokens: ~{response_tokens:,}")
                    print(f"  Total tokens:  ~{total_tokens:,}")
                    print(f"  Est. cost:     ~${total_tokens * 0.0000001:.6f}")
                    print("="*50 + "\n")
                except Exception as e:
                    logger.warning(f"Could not calculate token usage: {e}")
                
                yield {
                    "is_task_complete": True,
                    "content": final_response_content,
                }
                return

            if attempt <= max_retries:
                logger.warning(f"Retrying... ({attempt}/{max_retries + 1})")
                current_query_text = (
                    f"Your previous response was invalid. {error_message} "
                    "You MUST generate a valid response that strictly follows the A2UI JSON SCHEMA. "
                    f"Please retry the original request: '{query}'"
                )

        logger.error("Max retries exhausted. Sending text-only error.")
        yield {
            "is_task_complete": True,
            "content": "I'm sorry, I'm having trouble generating the interface. Please try again.",
        }

