def create_plan(user_query):

    query = user_query.lower()

    tools = []

    # Crop recommendation
    if (
        "crop" in query
        or "grow" in query
        or "cultivate" in query
    ):
        tools.append("crop_recommendation")

    # Weather
    if (
        "weather" in query
        or "rain" in query
        or "temperature" in query
        or "forecast" in query
    ):
        tools.append("weather")

    # Soil
    if (
        "soil" in query
        or "nitrogen" in query
        or "phosphorus" in query
        or "potassium" in query
        or "ph" in query
    ):
        tools.append("soil_analysis")

    # Disease
    if (
        "disease" in query
        or "leaf" in query
        or "spots" in query
        or "infection" in query
    ):
        tools.append("disease_detection")

    # Irrigation
    if (
        "irrigation" in query
        or "water" in query
        or "watering" in query
    ):
        tools.append("irrigation")

    return tools