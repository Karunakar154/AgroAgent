from typing import TypedDict


class AgroAgentState(TypedDict):

    user_query: str

    image_path: str

    latitude: float | None

    longitude: float | None

    farmer_context: dict

    plan: dict

    tool_results: dict

    verification: dict

    final_answer: str

    retry_count: int