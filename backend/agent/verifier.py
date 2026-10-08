def verify_results(tool_results):

    warnings = []


    # ==========================================
    # Weather + Irrigation
    # ==========================================

    if (
        "weather" in tool_results
        and "irrigation" in tool_results
    ):

        weather = tool_results["weather"]

        irrigation = tool_results["irrigation"]


        rain_probability = (
            weather["rain_probability"]
        )


        irrigation_decision = (
            irrigation["decision"]
        )


        if (
            rain_probability >= 70
            and "Irrigation" in irrigation_decision
        ):

            warnings.append(

                "Irrigation is recommended by the "
                "irrigation tool, but the probability "
                "of rain is high. The irrigation decision "
                "should be reviewed."
            )


    # ==========================================
    # Disease
    # ==========================================

    if "disease_detection" in tool_results:

        disease = (
            tool_results["disease_detection"]
        )


        if disease.get(
            "status"
        ) == "uncertain":

            warnings.append(

                "Disease prediction has low confidence. "
                "A clearer image or expert verification "
                "is recommended."
            )


    # ==========================================
    # Final Verification
    # ==========================================

    if not warnings:

        return {

            "status": "verified",

            "warnings": []
        }


    return {

        "status": "review_required",

        "warnings": warnings
    }