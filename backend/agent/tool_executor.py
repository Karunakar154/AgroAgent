from backend.tools.crop_tool import crop_recommendation_tool
from backend.tools.weather_tool import weather_tool
from backend.tools.soil_tool import soil_analysis_tool
from backend.tools.disease_tool import disease_detection_tool
from backend.tools.irrigation_tool import irrigation_tool
from backend.tools.agriculture_rag import agriculture_rag_tool


def execute_tool(
    tool_name,
    inputs
):

    if tool_name == "crop_recommendation":

        return crop_recommendation_tool(
            nitrogen=inputs["nitrogen"],
            phosphorus=inputs["phosphorus"],
            potassium=inputs["potassium"],
            temperature=inputs["temperature"],
            humidity=inputs["humidity"],
            ph=inputs["ph"],
            rainfall=inputs["rainfall"]
        )


    elif tool_name == "weather":

        return weather_tool(
            latitude=inputs["latitude"],
            longitude=inputs["longitude"]
        )


    elif tool_name == "soil_analysis":

        return soil_analysis_tool(
            nitrogen=inputs["nitrogen"],
            phosphorus=inputs["phosphorus"],
            potassium=inputs["potassium"],
            ph=inputs["ph"]
        )


    elif tool_name == "disease_detection":

        return disease_detection_tool(
            image_path=inputs["image_path"]
        )


    elif tool_name == "irrigation":

        return irrigation_tool(
            soil_moisture=inputs["soil_moisture"],
            temperature=inputs["temperature"],
            humidity=inputs["humidity"],
            rain_probability=inputs["rain_probability"]
        )


    elif tool_name == "agriculture_knowledge":

        return agriculture_rag_tool(
            query=inputs["query"]
        )


    else:

        return {
            "error":
            f"Unknown tool: {tool_name}"
        }