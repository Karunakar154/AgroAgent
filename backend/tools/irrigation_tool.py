def irrigation_tool(

    soil_moisture,

    temperature,

    humidity,

    rain_probability

):

    if rain_probability >= 70:

        decision = (
            "Do not irrigate"
        )

        reason = (
            "High probability of rain."
        )


    elif soil_moisture < 30:

        decision = (
            "Irrigation recommended"
        )

        reason = (
            "Soil moisture is low."
        )


    elif (
        temperature > 35
        and soil_moisture < 50
    ):

        decision = (
            "Light irrigation recommended"
        )

        reason = (
            "High temperature with "
            "moderate soil moisture."
        )


    else:

        decision = (
            "Irrigation not immediately required"
        )

        reason = (
            "Current conditions are acceptable."
        )


    return {

        "soil_moisture":
        soil_moisture,

        "temperature":
        temperature,

        "humidity":
        humidity,

        "rain_probability":
        rain_probability,

        "decision":
        decision,

        "reason":
        reason
    }