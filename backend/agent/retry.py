def retry_node(state):

    verification = state["verification"]

    warnings = verification.get(
        "warnings",
        []
    )


    current_retry_count = state.get(
        "retry_count",
        0
    )


    new_retry_count = (
        current_retry_count + 1
    )


    return {

        "user_query": (

            state["user_query"]

            + "\n\n"

            + "Previous verification warnings:\n"

            + "\n".join(warnings)

            + "\nPlease reconsider the decision."
        ),

        "retry_count":
        new_retry_count
    }