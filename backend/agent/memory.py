import re

from backend.database.memory_db import (
    save_memory,
    get_memory,
    delete_memory
)


# ==================================================
# EXTRACT SOIL VALUES
# ==================================================

def extract_soil_values(user_query):

    query = user_query.lower()

    soil = {}

    nitrogen_match = re.search(
        r"(?:nitrogen|n)\s*(?:=|:|is|of)?\s*(\d+(?:\.\d+)?)",
        query
    )

    if nitrogen_match:
        soil["nitrogen"] = float(
            nitrogen_match.group(1)
        )

    phosphorus_match = re.search(
        r"(?:phosphorus|phosphorous|p)\s*(?:=|:|is|of)?\s*(\d+(?:\.\d+)?)",
        query
    )

    if phosphorus_match:
        soil["phosphorus"] = float(
            phosphorus_match.group(1)
        )

    potassium_match = re.search(
        r"(?:potassium|k)\s*(?:=|:|is|of)?\s*(\d+(?:\.\d+)?)",
        query
    )

    if potassium_match:
        soil["potassium"] = float(
            potassium_match.group(1)
        )

    ph_match = re.search(
        r"\bph\s*(?:=|:|is|of)?\s*(\d+(?:\.\d+)?)",
        query
    )

    if ph_match:
        soil["ph"] = float(
            ph_match.group(1)
        )

    if not soil:
        return None

    return soil


# ==================================================
# SAVE CONVERSATION
# ==================================================

def save_conversation(
    session_id,
    user_query,
    latitude=None,
    longitude=None,
    tool_results=None,
    farmer_id=None,
    farm_id=None
):

    existing = get_memory(
        session_id
    )

    if existing:

        farmer_context = existing.get(
            "farmer_context",
            {}
        )

    else:

        farmer_context = {}


    # ==================================================
    # LOCATION
    # ==================================================

    if latitude is not None:

        farmer_context["latitude"] = latitude

    if longitude is not None:

        farmer_context["longitude"] = longitude


    # ==================================================
    # DIRECT SOIL INFORMATION
    # ==================================================

    soil_values = extract_soil_values(
        user_query
    )

    if soil_values:

        old_soil = farmer_context.get(
            "soil",
            {}
        )

        old_soil.update(
            soil_values
        )

        farmer_context["soil"] = old_soil


    # ==================================================
    # SOIL TOOL RESULT
    # ==================================================

    if tool_results:

        if "soil_analysis" in tool_results:

            soil = tool_results[
                "soil_analysis"
            ]

            farmer_context["soil"] = {

                "nitrogen":
                soil.get("nitrogen"),

                "phosphorus":
                soil.get("phosphorus"),

                "potassium":
                soil.get("potassium"),

                "ph":
                soil.get("ph")
            }


    # ==================================================
    # CROP MEMORY
    # ==================================================

    if tool_results:

        if "crop_recommendation" in tool_results:

            crop = tool_results[
                "crop_recommendation"
            ]

            farmer_context[
                "recommended_crop"
            ] = crop.get(
                "recommended_crop"
            )


    # ==================================================
    # WEATHER MEMORY
    # ==================================================

    if tool_results:

        if "weather" in tool_results:

            farmer_context[
                "latest_weather"
            ] = tool_results[
                "weather"
            ]


    # ==================================================
    # SAVE DATABASE MEMORY
    # ==================================================

    save_memory(

        session_id=session_id,

        user_query=user_query,

        farmer_context=farmer_context,

        tool_results=tool_results or {},

        farmer_id=farmer_id,

        farm_id=farm_id
    )


# ==================================================
# GET CONVERSATION
# ==================================================

def get_conversation(
    session_id
):

    return get_memory(
        session_id
    )


# ==================================================
# CLEAR CONVERSATION
# ==================================================

def clear_conversation(
    session_id
):

    delete_memory(
        session_id
    )