from backend.agent.llm_planner import create_plan
from backend.agent.agent_executor import execute_plan
from backend.agent.verifier import verify_results
from backend.agent.response_generator import generate_response
from backend.agent.retry import retry_node


# ==========================================
# Planner Node
# ==========================================

def planner_node(state):

    farmer_context = state.get(
        "farmer_context",
        {}
    )


    plan = create_plan(

        state["user_query"],

        state.get(
            "image_path"
        ),

        state.get(
            "latitude"
        ),

        state.get(
            "longitude"
        ),

        farmer_context
    )


    # ======================================
    # Debug: Farmer Memory
    # ======================================

    print("\n==============================")
    print("FARMER MEMORY")
    print("==============================")

    print(
        farmer_context
    )

    print("==============================\n")


    # ======================================
    # Debug: Location
    # ======================================

    print("\n==============================")
    print("LOCATION RECEIVED BY AGENT")
    print("==============================")

    print(
        "Latitude:",
        state.get("latitude")
    )

    print(
        "Longitude:",
        state.get("longitude")
    )

    print("==============================\n")


    # ======================================
    # Debug: Gemini Plan
    # ======================================

    print("\n==============================")
    print("GEMINI PLAN")
    print("==============================")

    print(
        plan
    )

    print("==============================\n")


    return {

        "plan":
        plan
    }


# ==========================================
# Tool Node
# ==========================================

def tool_node(state):

    plan = state["plan"]


    # ======================================
    # Inject Image Path
    # ======================================

    if state.get("image_path"):

        for tool in plan.get(
            "tools",
            []
        ):

            if tool["name"] == "disease_detection":

                tool["arguments"][
                    "image_path"
                ] = state[
                    "image_path"
                ]


    # ======================================
    # Inject Location
    # ======================================

    latitude = state.get(
        "latitude"
    )

    longitude = state.get(
        "longitude"
    )


    if (

        latitude is not None

        and longitude is not None
    ):

        for tool in plan.get(
            "tools",
            []
        ):

            if tool["name"] == "weather":

                tool["arguments"][
                    "latitude"
                ] = latitude

                tool["arguments"][
                    "longitude"
                ] = longitude


    # ======================================
    # Execute Tools
    # ======================================

    tool_results = execute_plan(
        plan
    )


    # ======================================
    # Debug: Tool Results
    # ======================================

    print("\n==============================")
    print("TOOL RESULTS")
    print("==============================")

    print(
        tool_results
    )

    print("==============================\n")


    return {

        "tool_results":
        tool_results
    }


# ==========================================
# Verifier Node
# ==========================================

def verifier_node(state):

    verification = verify_results(

        state[
            "tool_results"
        ]
    )


    # ======================================
    # Debug: Verification
    # ======================================

    print("\n==============================")
    print("VERIFICATION")
    print("==============================")

    print(
        verification
    )

    print("==============================\n")


    return {

        "verification":
        verification
    }


# ==========================================
# Response Node
# ==========================================

def response_node(state):

    final_answer = generate_response(

        state["user_query"],

        {

            "tool_results":
            state["tool_results"],

            "verification":
            state["verification"],

            "retry_count":
            state.get(
                "retry_count",
                0
            )
        }
    )


    return {

        "final_answer":
        final_answer
    }


# ==========================================
# Review Node
# ==========================================

def review_node(state):

    verification = state[
        "verification"
    ]


    warnings = verification.get(
        "warnings",
        []
    )


    message = (
        "The agent found some issues "
        "that need review:\n"
    )


    for warning in warnings:

        message += (
            f"- {warning}\n"
        )


    return {

        "final_answer":
        message
    }


# ==========================================
# Retry Node
# ==========================================

def retry_agent_node(state):

    return retry_node(
        state
    )