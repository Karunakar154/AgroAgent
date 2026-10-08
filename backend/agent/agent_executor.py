from backend.agent.tool_executor import execute_tool


def convert_value(value):

    if not isinstance(value, str):
        return value

    value = value.strip()

    value = value.replace("%", "")
    value = value.replace("°C", "")
    value = value.replace("°c", "")

    value = value.strip()

    try:

        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except ValueError:

        return value


def execute_plan(plan):

    results = {}


    # ==========================================
    # First pass
    # Execute weather and other independent tools
    # ==========================================

    for tool in plan.get("tools", []):

        tool_name = tool["name"]

        arguments = tool["arguments"]


        # Convert values

        for key in arguments:

            arguments[key] = convert_value(
                arguments[key]
            )


        # Crop waits for live weather

        if tool_name == "crop_recommendation":
            continue


        # Irrigation waits for weather

        if tool_name == "irrigation":
            continue


        # Execute tool

        try:

            result = execute_tool(
                tool_name,
                arguments
            )

            results[tool_name] = result


        except Exception as e:

            results[tool_name] = {

                "status": "error",

                "tool": tool_name,

                "error": str(e)
            }


    # ==========================================
    # Crop Recommendation
    # ==========================================

    for tool in plan.get("tools", []):

        if tool["name"] != "crop_recommendation":
            continue


        arguments = tool["arguments"]


        # --------------------------------------
        # Use LIVE weather data
        # --------------------------------------

        if "weather" in results:

            weather = results["weather"]


            arguments["temperature"] = (
                weather["current_temperature"]
            )


            arguments["humidity"] = (
                weather["current_humidity"]
            )


            # Open-Meteo gives precipitation
            # in mm. Use today's precipitation.

            arguments["rainfall"] = (
                weather["current_precipitation"]
            )


        # --------------------------------------
        # Convert values
        # --------------------------------------

        for key in arguments:

            arguments[key] = convert_value(
                arguments[key]
            )


        try:

            result = execute_tool(

                "crop_recommendation",

                arguments
            )

            results[
                "crop_recommendation"
            ] = result


        except Exception as e:

            results[
                "crop_recommendation"
            ] = {

                "status": "error",

                "tool":
                "crop_recommendation",

                "error":
                str(e)
            }


    # ==========================================
    # Irrigation
    # ==========================================

    for tool in plan.get("tools", []):

        if tool["name"] != "irrigation":
            continue


        arguments = tool["arguments"]


        # --------------------------------------
        # Use live weather
        # --------------------------------------

        if "weather" in results:

            weather = results["weather"]


            arguments["temperature"] = (
                weather["current_temperature"]
            )


            arguments["humidity"] = (
                weather["current_humidity"]
            )


            arguments["rain_probability"] = (
                weather["rain_probability"]
            )


        # --------------------------------------
        # Convert values
        # --------------------------------------

        for key in arguments:

            arguments[key] = convert_value(
                arguments[key]
            )


        try:

            result = execute_tool(

                "irrigation",

                arguments
            )

            results[
                "irrigation"
            ] = result


        except Exception as e:

            results[
                "irrigation"
            ] = {

                "status": "error",

                "tool":
                "irrigation",

                "error":
                str(e)
            }


    return results