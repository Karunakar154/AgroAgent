import os
import json
import re

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def extract_soil_values(user_query):
    """
    Extract N, P, K and pH values from the farmer's message.
    """

    text = user_query.lower()

    values = {}

    patterns = {
        "nitrogen": [
            r"nitrogen\s*(?:=|is|:)?\s*(\d+(?:\.\d+)?)",
            r"\bn\s*(?:=|is|:)?\s*(\d+(?:\.\d+)?)"
        ],

        "phosphorus": [
            r"phosphorus\s*(?:=|is|:)?\s*(\d+(?:\.\d+)?)",
            r"\bp\s*(?:=|is|:)?\s*(\d+(?:\.\d+)?)"
        ],

        "potassium": [
            r"potassium\s*(?:=|is|:)?\s*(\d+(?:\.\d+)?)",
            r"\bk\s*(?:=|is|:)?\s*(\d+(?:\.\d+)?)"
        ],

        "ph": [
            r"ph\s*(?:=|is|:)?\s*(\d+(?:\.\d+)?)"
        ]
    }

    for key, pattern_list in patterns.items():

        for pattern in pattern_list:

            match = re.search(pattern, text)

            if match:
                values[key] = float(match.group(1))
                break

    return values


def create_plan(
    user_query,
    image_path=None,
    latitude=None,
    longitude=None,
    farmer_context=None
):

    farmer_context = farmer_context or {}

    query = user_query.lower()


    # ==================================================
    # EXTRACT CURRENT SOIL INFORMATION
    # ==================================================

    current_soil = extract_soil_values(user_query)

    # Merge current values into memory
    updated_context = dict(farmer_context)

    for key, value in current_soil.items():
        updated_context[key] = value


    # ==================================================
    # WEATHER DETECTION
    # ==================================================

    weather_keywords = [
        "weather",
        "rain",
        "rainfall",
        "forecast",
        "temperature",
        "humidity",
        "climate",
        "raining",
        "will it rain",
        "rain tomorrow",
        "weather tomorrow"
    ]

    weather_requested = any(
        word in query
        for word in weather_keywords
    )


    # ==================================================
    # IMAGE
    # ==================================================

    image_instruction = ""

    if image_path:

        image_instruction = """
An image has been uploaded.

If the farmer asks about:

- plant disease
- leaf disease
- spots
- infection
- leaf problems
- plant health

select disease_detection.

Also select agriculture_knowledge when
additional agricultural information is useful.
"""


    # ==================================================
    # LOCATION
    # ==================================================

    if (
        latitude is not None
        and longitude is not None
    ):

        location_instruction = f"""
Application farm location:

latitude = {latitude}
longitude = {longitude}

Use these exact coordinates for weather.

Never invent coordinates.
"""

    else:

        location_instruction = """
Farm location is unavailable.

Never invent coordinates.
"""


    # ==================================================
    # MEMORY
    # ==================================================

    memory_instruction = f"""
REMEMBERED FARMER INFORMATION:

{json.dumps(
    updated_context,
    indent=2
)}

IMPORTANT MEMORY RULES:

1. Current information has priority.

2. If the current message contains a new
   soil value, update the remembered value.

3. If the current message contains only some
   soil values, keep the previously remembered
   values for the other soil parameters.

4. Never delete previously remembered values
   unless the farmer explicitly gives a new value.

5. Never invent missing values.
"""


    # ==================================================
    # PROMPT
    # ==================================================

    prompt = f"""
You are the planning brain of AgroAgent,
an autonomous AI agriculture assistant.

Your job is to understand the farmer's intent,
use remembered information, identify missing
information, and select the correct tools.

AVAILABLE TOOLS:

1. crop_recommendation

Arguments:

nitrogen
phosphorus
potassium
temperature
humidity
ph
rainfall


2. weather

Arguments:

latitude
longitude


3. soil_analysis

Arguments:

nitrogen
phosphorus
potassium
ph


4. disease_detection

Arguments:

image_path


5. irrigation

Arguments:

soil_moisture
temperature
humidity
rain_probability


6. agriculture_knowledge

Arguments:

query


==================================================
CROP RECOMMENDATION
==================================================

Required parameters:

nitrogen
phosphorus
potassium
temperature
humidity
ph
rainfall

VERY IMPORTANT:

The crop recommendation tool must NEVER
receive invented soil values.

Use:

- current soil values from the farmer
- remembered soil values
- weather tool for temperature, humidity
  and rainfall when farm coordinates exist

If all soil values are available but weather
values are missing and coordinates exist:

SELECT BOTH:

weather
crop_recommendation

The weather result will provide:

temperature
humidity
rainfall

Then crop recommendation can use those values.


==================================================
PARTIAL SOIL INFORMATION
==================================================

If the farmer provides only some values,
remember them.

Example:

Farmer:

"N=20 P=60 K=85"

Remember:

nitrogen = 20
phosphorus = 60
potassium = 85

Do NOT recommend a crop yet if pH is missing.

Return:

status = "missing_information"

missing_information = ["ph"]


Example:

Farmer previously provided:

N = 20
P = 60
K = 85

Current message:

"pH is 6.5"

Combine them:

N = 20
P = 60
K = 85
pH = 6.5

Do NOT ask for N/P/K again.


==================================================
WEATHER
==================================================

Select weather when:

- weather is explicitly requested
- weather is required for crop recommendation
- weather is required for irrigation

Use the application farm coordinates.

Never invent coordinates.


==================================================
SOIL ANALYSIS
==================================================

Required:

nitrogen
phosphorus
potassium
ph

Use current or remembered values.

If all four are available,
select soil_analysis when the farmer
asks for soil analysis.

Never invent values.


==================================================
IRRIGATION
==================================================

Required:

soil_moisture
temperature
humidity
rain_probability

Weather can provide:

temperature
humidity
rain_probability

Never invent soil moisture.


==================================================
DISEASE DETECTION
==================================================

If an image exists and the farmer asks about:

- disease
- leaf problems
- spots
- infection
- plant health

select disease_detection.


==================================================
GENERAL AGRICULTURE KNOWLEDGE
==================================================

Use agriculture_knowledge for general
agriculture questions.

Examples:

"What causes leaf spots?"

"How do I improve soil pH?"

"How should I prevent crop disease?"


==================================================
NO INVENTION
==================================================

Never invent:

- nitrogen
- phosphorus
- potassium
- pH
- temperature
- humidity
- rainfall
- soil moisture
- coordinates
- image paths


==================================================
MEMORY
==================================================

{memory_instruction}


==================================================
LOCATION
==================================================

{location_instruction}


==================================================
IMAGE
==================================================

{image_instruction}


==================================================
CURRENT FARMER REQUEST
==================================================

{user_query}


==================================================
OUTPUT
==================================================

Return ONLY valid JSON.

If required information is missing:

{{
    "status": "missing_information",

    "tools": [],

    "missing_information": [
        "ph"
    ]
}}

If enough information exists:

{{
    "status": "ready",

    "tools": [
        {{
            "name": "weather",

            "arguments": {{
                "latitude": {latitude},
                "longitude": {longitude}
            }}
        }},

        {{
            "name": "crop_recommendation",

            "arguments": {{
                "nitrogen": 20,
                "phosphorus": 60,
                "potassium": 85,
                "temperature": 0,
                "humidity": 0,
                "ph": 6.5,
                "rainfall": 0
            }}
        }}
    ],

    "missing_information": []
}}

IMPORTANT:

The example weather values above are placeholders
only for explaining the JSON structure.

Do NOT use placeholder values in the actual plan.

Return only JSON.
"""


    # ==================================================
    # GEMINI
    # ==================================================

    response = client.models.generate_content(

        model="gemini-3.5-flash-lite",

        contents=prompt
    )


    result = response.text.strip()


    # ==================================================
    # CLEAN JSON
    # ==================================================

    if result.startswith("```json"):
        result = result[7:]

    if result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    result = result.strip()


    plan = json.loads(result)


    # ==================================================
    # FORCE WEATHER WHEN EXPLICITLY REQUESTED
    # ==================================================

    if (
        weather_requested
        and latitude is not None
        and longitude is not None
    ):

        weather_exists = any(

            tool.get("name") == "weather"

            for tool in plan.get(
                "tools",
                []
            )
        )

        if not weather_exists:

            plan.setdefault(
                "tools",
                []
            ).append({

                "name": "weather",

                "arguments": {

                    "latitude": latitude,

                    "longitude": longitude
                }
            })


    return plan