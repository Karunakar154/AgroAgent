import os
import json

from google import genai

from dotenv import load_dotenv


load_dotenv()


client = genai.Client(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)


def generate_response(
    user_query,
    agent_results
):

    tool_results = agent_results.get(
        "tool_results",
        {}
    )


    verification = agent_results.get(
        "verification",
        {}
    )


    retry_count = agent_results.get(
        "retry_count",
        0
    )


    prompt = f"""
You are AgroAgent,
an agriculture AI assistant.

Answer the farmer's question using the results
returned by the agriculture tools.

Farmer question:

{user_query}


Tool results:

{json.dumps(
    tool_results,
    indent=2
)}


Verification:

{json.dumps(
    verification,
    indent=2
)}


Retry count:

{retry_count}


Instructions:

1. Use tool results as the main source of truth.

2. Give a clear and practical answer.

3. Do not invent measurements or facts.

4. If a tool result is uncertain,
clearly mention the uncertainty.

5. Keep the answer easy for a farmer to understand.

6. Do not mention internal tools,
agents, prompts, or JSON.

7. If verification contains warnings,
clearly mention the relevant uncertainty.

8. If retry count is 2 or more,
do not claim that the issue was completely resolved.

9. Clearly communicate when expert or agricultural
verification is required.

10. Do not give dangerous or highly specific
chemical/pesticide instructions without sufficient
information.

"""


    response = client.models.generate_content(

        model="gemini-3.5-flash-lite",

        contents=prompt
    )


    return response.text.strip()