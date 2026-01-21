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

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_parts_message,
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from a2ui.a2ui_extension import create_a2ui_part, try_activate_a2ui_extension
from agent import HotelAgent

logger = logging.getLogger(__name__)


class HotelAgentExecutor(AgentExecutor):
    """Hotel AgentExecutor for A2UI integration."""

    def __init__(self, base_url: str):
        self.ui_agent = HotelAgent(base_url=base_url, use_ui=True)
        self.text_agent = HotelAgent(base_url=base_url, use_ui=False)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = ""
        ui_event_part = None
        action = None

        logger.info(f"--- Client requested extensions: {context.requested_extensions} ---")
        use_ui = try_activate_a2ui_extension(context)

        if use_ui:
            agent = self.ui_agent
            logger.info("--- AGENT_EXECUTOR: A2UI extension is active. Using UI agent. ---")
        else:
            agent = self.text_agent
            logger.info("--- AGENT_EXECUTOR: A2UI extension is not active. Using text agent. ---")

        if context.message and context.message.parts:
            logger.info(f"--- AGENT_EXECUTOR: Processing {len(context.message.parts)} message parts ---")
            for i, part in enumerate(context.message.parts):
                if isinstance(part.root, DataPart):
                    if "userAction" in part.root.data:
                        logger.info(f"  Part {i}: Found A2UI ClientEvent payload.")
                        ui_event_part = part.root.data["userAction"]
                    else:
                        logger.info(f"  Part {i}: DataPart (data: {part.root.data})")
                elif isinstance(part.root, TextPart):
                    logger.info(f"  Part {i}: TextPart (text: {part.root.text})")
                else:
                    logger.info(f"  Part {i}: Unknown part type ({type(part.root)})")

        if ui_event_part:
            logger.info(f"Received A2UI ClientEvent: {ui_event_part}")
            action = ui_event_part.get("actionName")
            ctx = ui_event_part.get("context", {})

            if action == "view_hotel_details":
                hotel_code = ctx.get("hotelCode", "Unknown")
                hotel_name = ctx.get("hotelName", "Unknown Hotel")
                query = f"USER_WANTS_TO_VIEW_HOTEL: hotelCode={hotel_code}, hotelName={hotel_name}. Please call get_resort_details and get_hotel_availability tools to show the hotel details and available rooms."

            elif action == "book_room":
                hotel_code = ctx.get("hotelCode", "Unknown")
                hotel_name = ctx.get("hotelName", "Unknown Hotel")
                room_type_code = ctx.get("roomTypeCode", "Unknown")
                room_name = ctx.get("roomName", "Unknown Room")
                price = ctx.get("price", 0)
                query = f"USER_BOOKED_ROOM: hotelName={hotel_name}, roomName={room_name}, roomTypeCode={room_type_code}, pricePerNight=${price}. Please confirm this booking for dates Feb 1-5, 2026 (4 nights)."

            else:
                query = f"User submitted an event: {action} with data: {ctx}"
        else:
            logger.info("No A2UI event part found. Falling back to text input.")
            query = context.get_user_input()

        logger.info(f"--- AGENT_EXECUTOR: Final query for LLM: '{query}' ---")

        task = context.current_task

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        async for item in agent.stream(query, task.context_id):
            is_task_complete = item["is_task_complete"]
            if not is_task_complete:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(item["updates"], task.context_id, task.id),
                )
                continue

            final_state = (
                TaskState.completed
                if action == "book_room"
                else TaskState.input_required
            )

            content = item["content"]
            final_parts = []
            
            if "---a2ui_JSON---" in content:
                logger.info("Splitting final response into text and UI parts.")
                text_content, json_string = content.split("---a2ui_JSON---", 1)

                if text_content.strip():
                    final_parts.append(Part(root=TextPart(text=text_content.strip())))

                if json_string.strip():
                    try:
                        json_string_cleaned = (
                            json_string.strip().lstrip("```json").rstrip("```").strip()
                        )
                        json_data = json.loads(json_string_cleaned)

                        if isinstance(json_data, list):
                            logger.info(f"Found {len(json_data)} messages. Creating individual DataParts.")
                            for message in json_data:
                                final_parts.append(create_a2ui_part(message))
                        else:
                            logger.info("Received a single JSON object. Creating a DataPart.")
                            final_parts.append(create_a2ui_part(json_data))

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse UI JSON: {e}")
                        final_parts.append(Part(root=TextPart(text=json_string)))
            else:
                final_parts.append(Part(root=TextPart(text=content.strip())))

            logger.info("--- FINAL PARTS TO BE SENT ---")
            for i, part in enumerate(final_parts):
                logger.info(f"  - Part {i}: Type = {type(part.root)}")
                if isinstance(part.root, TextPart):
                    logger.info(f"    - Text: {part.root.text[:200]}...")
                elif isinstance(part.root, DataPart):
                    logger.info(f"    - Data: {str(part.root.data)[:200]}...")
            logger.info("-----------------------------")

            await updater.update_status(
                final_state,
                new_agent_parts_message(final_parts, task.context_id, task.id),
                final=(final_state == TaskState.completed),
            )
            break

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())

