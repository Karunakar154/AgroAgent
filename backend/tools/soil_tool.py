def soil_analysis_tool(

    nitrogen,

    phosphorus,

    potassium,

    ph

):

    issues = []

    recommendations = []


    # ==========================================
    # Nitrogen
    # ==========================================

    if nitrogen < 40:

        issues.append(
            "Low nitrogen"
        )

        recommendations.append(
            "Consider improving nitrogen availability."
        )


    elif nitrogen > 140:

        issues.append(
            "High nitrogen"
        )

        recommendations.append(
            "Avoid excessive nitrogen application."
        )


    # ==========================================
    # Phosphorus
    # ==========================================

    if phosphorus < 20:

        issues.append(
            "Low phosphorus"
        )

        recommendations.append(
            "Consider improving phosphorus availability."
        )


    elif phosphorus > 100:

        issues.append(
            "High phosphorus"
        )

        recommendations.append(
            "Avoid excessive phosphorus application."
        )


    # ==========================================
    # Potassium
    # ==========================================

    if potassium < 20:

        issues.append(
            "Low potassium"
        )

        recommendations.append(
            "Consider improving potassium availability."
        )


    elif potassium > 150:

        issues.append(
            "High potassium"
        )

        recommendations.append(
            "Avoid excessive potassium application."
        )


    # ==========================================
    # pH
    # ==========================================

    if ph < 5.5:

        issues.append(
            "Acidic soil"
        )

        recommendations.append(
            "Consider appropriate soil pH management."
        )


    elif ph > 8.0:

        issues.append(
            "Alkaline soil"
        )

        recommendations.append(
            "Consider appropriate soil pH management."
        )


    # ==========================================
    # No Issues
    # ==========================================

    if not issues:

        issues.append(
            "No major issue detected"
        )

        recommendations.append(
            "Soil parameters appear to be within "
            "the expected range."
        )


    return {

        "nitrogen":
        nitrogen,

        "phosphorus":
        phosphorus,

        "potassium":
        potassium,

        "ph":
        ph,

        "issues":
        issues,

        "recommendations":
        recommendations
    }