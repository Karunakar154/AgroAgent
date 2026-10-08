def verification_decision(state):

    verification = state["verification"]

    retry_count = state.get(
        "retry_count",
        0
    )


    print("\n--- VERIFICATION DECISION ---")

    print(
        "Status:",
        verification["status"]
    )

    print(
        "Retry Count:",
        retry_count
    )


    if verification["status"] == "verified":

        print(
            "Decision: RESPONSE"
        )

        return "response"


    if retry_count < 2:

        print(
            "Decision: REVIEW"
        )

        return "review"


    print(
        "Decision: RESPONSE (MAX RETRIES)"
    )

    return "response"