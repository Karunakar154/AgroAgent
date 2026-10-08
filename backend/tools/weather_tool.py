import requests


def weather_tool(
    latitude,
    longitude
):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "current":
        "temperature_2m,relative_humidity_2m,precipitation,weather_code",

        "daily":
        "temperature_2m_max,"
        "temperature_2m_min,"
        "precipitation_sum,"
        "precipitation_probability_max",

        "forecast_days": 7,

        "timezone": "auto"
    }


    response = requests.get(

        url,

        params=params,

        timeout=10
    )


    response.raise_for_status()


    data = response.json()


    # ==========================================
    # Current Weather
    # ==========================================

    current_temperature = (
        data["current"]["temperature_2m"]
    )

    current_humidity = (
        data["current"]["relative_humidity_2m"]
    )

    current_precipitation = (
        data["current"]["precipitation"]
    )


    # ==========================================
    # Daily Weather
    # ==========================================

    daily_rainfall = (
        data["daily"]["precipitation_sum"]
    )

    rain_probability = (
        data["daily"]["precipitation_probability_max"]
    )


    # ==========================================
    # Calculate Rainfall
    # ==========================================

    today_rainfall = daily_rainfall[0]

    seven_day_rainfall = sum(
        daily_rainfall
    )


    # ==========================================
    # Return Weather Information
    # ==========================================

    return {

        "current_temperature":
        current_temperature,

        "current_humidity":
        current_humidity,

        "current_precipitation":
        current_precipitation,

        "today_max_temperature":
        data["daily"]["temperature_2m_max"][0],

        "today_min_temperature":
        data["daily"]["temperature_2m_min"][0],

        "today_rainfall":
        today_rainfall,

        "seven_day_rainfall":
        round(
            seven_day_rainfall,
            2
        ),

        "rain_probability":
        rain_probability[0]
    }