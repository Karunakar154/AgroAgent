from agent.llm_planner import create_plan
from agent.agent_executor import execute_plan
from agent.response_generator import generate_response

from agent.memory import (
    save_conversation,
    get_conversation,
    clear_conversation
)

from agent.verifier import verify_results


def run_agent(user_query, session_id):

    # Check previous conversation
    previous = get_conversation(session_id)

    if previous:

        combined_query = f"""
Previous farmer question:
{previous['user_query']}

Farmer's latest response:
{user_query}
"""

    else:

        combined_query = user_query


    # Step 1: Create plan
    plan = create_plan(combined_query)

    print("\nGemini Plan:")
    print(plan)


    # Step 2: Check missing information
    if plan["status"] == "needs_input":

        save_conversation(
            session_id,
            combined_query,
            plan
        )

        missing = plan["missing_information"]

        questions = {
            "soil_moisture": "What is the current soil moisture percentage?",
            "temperature": "What is the current temperature?",
            "humidity": "What is the current humidity percentage?",
            "rain_probability": "What is the probability of rain?",
            "nitrogen": "What is the nitrogen level in the soil?",
            "phosphorus": "What is the phosphorus level in the soil?",
            "potassium": "What is the potassium level in the soil?",
            "ph": "What is the soil pH?"
        }

        response = "I need some additional information:\n"

        for item in missing:

            response += f"- {questions.get(item, item)}\n"

        return response


    # Step 3: Execute tools
    tool_results = execute_plan(plan)

    print("\nTool Results:")
    print(tool_results)


    # Step 4: Verify tool results
    verification = verify_results(tool_results)

    print("\nVerification:")
    print(verification)


    # Step 5: Generate final answer
    final_answer = generate_response(
        combined_query,
        {
            "tool_results": tool_results,
            "verification": verification
        }
    )


    # Conversation completed
    clear_conversation(session_id)

    return final_answer