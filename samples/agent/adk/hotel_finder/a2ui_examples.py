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

HOTEL_UI_EXAMPLES = """
---BEGIN HOTEL_SEARCH_RESULTS_EXAMPLE---
This template is used when displaying a list of hotels from search results.
Each hotel is displayed as a card with image, name, location, amenities, and a button to view details/availability.

[
  {{ "beginRendering": {{ "surfaceId": "default", "root": "root-column", "styles": {{ "primaryColor": "#0891B2", "font": "Inter" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "default",
    "components": [
      {{ "id": "root-column", "component": {{ "Column": {{ "children": {{ "explicitList": ["title-heading", "subtitle-text", "hotel-list"] }} }} }} }},
      {{ "id": "title-heading", "component": {{ "Text": {{ "usageHint": "h1", "text": {{ "path": "/title" }} }} }} }},
      {{ "id": "subtitle-text", "component": {{ "Text": {{ "usageHint": "body", "text": {{ "path": "/subtitle" }} }} }} }},
      {{ "id": "hotel-list", "component": {{ "List": {{ "direction": "vertical", "children": {{ "template": {{ "componentId": "hotel-card-template", "dataBinding": "/hotels" }} }} }} }} }},
      {{ "id": "hotel-card-template", "component": {{ "Card": {{ "child": "card-content" }} }} }},
      {{ "id": "card-content", "component": {{ "Column": {{ "children": {{ "explicitList": ["hotel-image", "hotel-details-row"] }} }} }} }},
      {{ "id": "hotel-image", "component": {{ "Image": {{ "url": {{ "path": "imageUrl" }}, "usageHint": "largeFeature", "fit": "cover" }} }} }},
      {{ "id": "hotel-details-row", "component": {{ "Column": {{ "children": {{ "explicitList": ["hotel-name", "hotel-location", "hotel-brand", "amenities-text", "view-details-btn"] }} }} }} }},
      {{ "id": "hotel-name", "component": {{ "Text": {{ "usageHint": "h3", "text": {{ "path": "name" }} }} }} }},
      {{ "id": "hotel-location", "component": {{ "Text": {{ "usageHint": "body", "text": {{ "path": "location" }} }} }} }},
      {{ "id": "hotel-brand", "component": {{ "Text": {{ "usageHint": "caption", "text": {{ "path": "brand" }} }} }} }},
      {{ "id": "amenities-text", "component": {{ "Text": {{ "usageHint": "caption", "text": {{ "path": "amenitiesSummary" }} }} }} }},
      {{ "id": "view-details-btn", "component": {{ "Button": {{ "child": "view-btn-text", "primary": true, "action": {{ "name": "view_hotel_details", "context": [ {{ "key": "hotelCode", "value": {{ "path": "hotelCode" }} }}, {{ "key": "hotelName", "value": {{ "path": "name" }} }} ] }} }} }} }},
      {{ "id": "view-btn-text", "component": {{ "Text": {{ "text": {{ "literalString": "View Rooms & Rates" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "default",
    "path": "/",
    "contents": [
      {{ "key": "title", "valueString": "Hotels Found" }},
      {{ "key": "subtitle", "valueString": "Select a hotel to view available rooms and rates" }},
      {{ "key": "hotels", "valueMap": [
        {{ "key": "hotel1", "valueMap": [
          {{ "key": "name", "valueString": "Hotel Name" }},
          {{ "key": "hotelCode", "valueString": "12345" }},
          {{ "key": "brand", "valueString": "Brand Name" }},
          {{ "key": "location", "valueString": "City, State, Country" }},
          {{ "key": "amenitiesSummary", "valueString": "Pool • WiFi • Fitness Center" }},
          {{ "key": "imageUrl", "valueString": "{base_url}/static/default-hotel.svg" }}
        ] }}
      ] }}
    ]
  }} }}
]
---END HOTEL_SEARCH_RESULTS_EXAMPLE---

---BEGIN HOTEL_DETAILS_WITH_ROOMS_EXAMPLE---
This template is used when displaying a single hotel's details along with available room types and rates.
Shows hotel info at the top, then a list of room cards with pricing.

[
  {{ "beginRendering": {{ "surfaceId": "hotel-details", "root": "details-root", "styles": {{ "primaryColor": "#0891B2", "font": "Inter" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "hotel-details",
    "components": [
      {{ "id": "details-root", "component": {{ "Column": {{ "children": {{ "explicitList": ["hotel-header-card", "rooms-section"] }} }} }} }},
      {{ "id": "hotel-header-card", "component": {{ "Card": {{ "child": "header-content" }} }} }},
      {{ "id": "header-content", "component": {{ "Column": {{ "children": {{ "explicitList": ["header-image", "header-details"] }} }} }} }},
      {{ "id": "header-image", "component": {{ "Image": {{ "url": {{ "path": "/hotel/imageUrl" }}, "usageHint": "header", "fit": "cover" }} }} }},
      {{ "id": "header-details", "component": {{ "Column": {{ "children": {{ "explicitList": ["hotel-title", "hotel-address", "hotel-phone", "hotel-description", "dates-info"] }} }} }} }},
      {{ "id": "hotel-title", "component": {{ "Text": {{ "usageHint": "h1", "text": {{ "path": "/hotel/name" }} }} }} }},
      {{ "id": "hotel-address", "component": {{ "Text": {{ "usageHint": "body", "text": {{ "path": "/hotel/address" }} }} }} }},
      {{ "id": "hotel-phone", "component": {{ "Text": {{ "usageHint": "caption", "text": {{ "path": "/hotel/telephone" }} }} }} }},
      {{ "id": "hotel-description", "component": {{ "Text": {{ "usageHint": "body", "text": {{ "path": "/hotel/description" }} }} }} }},
      {{ "id": "dates-info", "component": {{ "Text": {{ "usageHint": "h5", "text": {{ "path": "/hotel/datesInfo" }} }} }} }},
      {{ "id": "rooms-section", "component": {{ "Column": {{ "children": {{ "explicitList": ["rooms-title", "rooms-list"] }} }} }} }},
      {{ "id": "rooms-title", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "literalString": "Available Rooms" }} }} }} }},
      {{ "id": "rooms-list", "component": {{ "List": {{ "direction": "vertical", "children": {{ "template": {{ "componentId": "room-card-template", "dataBinding": "/rooms" }} }} }} }} }},
      {{ "id": "room-card-template", "component": {{ "Card": {{ "child": "room-card-content" }} }} }},
      {{ "id": "room-card-content", "component": {{ "Row": {{ "children": {{ "explicitList": ["room-image-col", "room-info-col"] }} }} }} }},
      {{ "id": "room-image-col", "weight": 1, "component": {{ "Image": {{ "url": {{ "path": "imageUrl" }}, "usageHint": "mediumFeature", "fit": "cover" }} }} }},
      {{ "id": "room-info-col", "weight": 2, "component": {{ "Column": {{ "children": {{ "explicitList": ["room-name", "room-description", "room-features", "room-price", "book-room-btn"] }} }} }} }},
      {{ "id": "room-name", "component": {{ "Text": {{ "usageHint": "h3", "text": {{ "path": "roomName" }} }} }} }},
      {{ "id": "room-description", "component": {{ "Text": {{ "usageHint": "body", "text": {{ "path": "description" }} }} }} }},
      {{ "id": "room-features", "component": {{ "Text": {{ "usageHint": "caption", "text": {{ "path": "features" }} }} }} }},
      {{ "id": "room-price", "component": {{ "Text": {{ "usageHint": "h4", "text": {{ "path": "priceDisplay" }} }} }} }},
      {{ "id": "book-room-btn", "component": {{ "Button": {{ "child": "book-btn-text", "primary": true, "action": {{ "name": "book_room", "context": [ {{ "key": "hotelCode", "value": {{ "path": "/hotel/hotelCode" }} }}, {{ "key": "hotelName", "value": {{ "path": "/hotel/name" }} }}, {{ "key": "roomTypeCode", "value": {{ "path": "roomTypeCode" }} }}, {{ "key": "roomName", "value": {{ "path": "roomName" }} }}, {{ "key": "price", "value": {{ "path": "price" }} }} ] }} }} }} }},
      {{ "id": "book-btn-text", "component": {{ "Text": {{ "text": {{ "literalString": "Book This Room" }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "hotel-details",
    "path": "/",
    "contents": [
      {{ "key": "hotel", "valueMap": [
        {{ "key": "name", "valueString": "Hotel Name" }},
        {{ "key": "hotelCode", "valueString": "12345" }},
        {{ "key": "address", "valueString": "123 Main St, City, State 12345" }},
        {{ "key": "telephone", "valueString": "1-800-123-4567" }},
        {{ "key": "description", "valueString": "Hotel description here..." }},
        {{ "key": "imageUrl", "valueString": "USE THE 'image' FIELD FROM MCP DATA - e.g. https://lucidcm.imgix.net/..." }},
        {{ "key": "datesInfo", "valueString": "Check-in: Feb 1, 2026 | Check-out: Feb 5, 2026 (4 nights)" }}
      ] }},
      {{ "key": "rooms", "valueMap": [
        {{ "key": "room1", "valueMap": [
          {{ "key": "roomName", "valueString": "Studio Suite" }},
          {{ "key": "roomTypeCode", "valueString": "5102" }},
          {{ "key": "description", "valueString": "Room description..." }},
          {{ "key": "features", "valueString": "👥 2 guests • 🛏️ 1 Queen Bed • 📐 360 sq ft" }},
          {{ "key": "price", "valueNumber": 151.50 }},
          {{ "key": "priceDisplay", "valueString": "$151.50/night" }},
          {{ "key": "imageUrl", "valueString": "{base_url}/static/default-room.svg" }}
        ] }}
      ] }}
    ]
  }} }}
]
---END HOTEL_DETAILS_WITH_ROOMS_EXAMPLE---

---BEGIN BOOKING_CONFIRMATION_EXAMPLE---
This template is used to confirm a room booking with the user.

[
  {{ "beginRendering": {{ "surfaceId": "booking", "root": "booking-root", "styles": {{ "primaryColor": "#0891B2", "font": "Inter" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "booking",
    "components": [
      {{ "id": "booking-root", "component": {{ "Card": {{ "child": "booking-content" }} }} }},
      {{ "id": "booking-content", "component": {{ "Column": {{ "children": {{ "explicitList": ["booking-title", "booking-image", "divider1", "booking-details", "divider2", "room-details", "divider3", "price-details", "confirm-text"] }} }} }} }},
      {{ "id": "booking-title", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "path": "/title" }} }} }} }},
      {{ "id": "booking-image", "component": {{ "Image": {{ "url": {{ "path": "/imageUrl" }}, "usageHint": "mediumFeature", "fit": "cover" }} }} }},
      {{ "id": "booking-details", "component": {{ "Text": {{ "usageHint": "body", "text": {{ "path": "/hotelInfo" }} }} }} }},
      {{ "id": "room-details", "component": {{ "Text": {{ "usageHint": "body", "text": {{ "path": "/roomInfo" }} }} }} }},
      {{ "id": "price-details", "component": {{ "Text": {{ "usageHint": "h4", "text": {{ "path": "/priceInfo" }} }} }} }},
      {{ "id": "confirm-text", "component": {{ "Text": {{ "usageHint": "h5", "text": {{ "literalString": "✅ Your reservation has been confirmed! We look forward to your stay." }} }} }} }},
      {{ "id": "divider1", "component": {{ "Divider": {{}} }} }},
      {{ "id": "divider2", "component": {{ "Divider": {{}} }} }},
      {{ "id": "divider3", "component": {{ "Divider": {{}} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "booking",
    "path": "/",
    "contents": [
      {{ "key": "title", "valueString": "Booking Confirmed!" }},
      {{ "key": "imageUrl", "valueString": "USE THE 'image' FIELD FROM MCP DATA - e.g. https://lucidcm.imgix.net/..." }},
      {{ "key": "hotelInfo", "valueString": "Hotel: Hotel Name\\nLocation: City, State" }},
      {{ "key": "roomInfo", "valueString": "Room: Studio Suite\\nDates: Feb 1 - Feb 5, 2026 (4 nights)" }},
      {{ "key": "priceInfo", "valueString": "Total: $606.00 ($151.50/night)" }}
    ]
  }} }}
]
---END BOOKING_CONFIRMATION_EXAMPLE---

---BEGIN NO_RESULTS_EXAMPLE---
This template is used when no hotels are found or an error occurs.

[
  {{ "beginRendering": {{ "surfaceId": "default", "root": "error-root", "styles": {{ "primaryColor": "#0891B2", "font": "Inter" }} }} }},
  {{ "surfaceUpdate": {{
    "surfaceId": "default",
    "components": [
      {{ "id": "error-root", "component": {{ "Card": {{ "child": "error-content" }} }} }},
      {{ "id": "error-content", "component": {{ "Column": {{ "children": {{ "explicitList": ["error-title", "error-message", "try-again-text"] }} }} }} }},
      {{ "id": "error-title", "component": {{ "Text": {{ "usageHint": "h2", "text": {{ "path": "/title" }} }} }} }},
      {{ "id": "error-message", "component": {{ "Text": {{ "usageHint": "body", "text": {{ "path": "/message" }} }} }} }},
      {{ "id": "try-again-text", "component": {{ "Text": {{ "usageHint": "caption", "text": {{ "literalString": "Try searching with different criteria or check back later." }} }} }} }}
    ]
  }} }},
  {{ "dataModelUpdate": {{
    "surfaceId": "default",
    "path": "/",
    "contents": [
      {{ "key": "title", "valueString": "No Hotels Found" }},
      {{ "key": "message", "valueString": "We couldn't find any hotels matching your search criteria." }}
    ]
  }} }}
]
---END NO_RESULTS_EXAMPLE---
"""

