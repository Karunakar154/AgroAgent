from backend.agent.llm_planner import create_plan
from backend.agent.agent_executor import execute_plan


query = """
Previous farmer message:
Should I irrigate my field?

Latest farmer message:
Soil moisture is 25%, temperature is 32°C,
humidity is 60%, and rain probability is 20%.
"""


print("\n==============================")
print("TESTING MEMORY QUERY")
print("==============================")


plan = create_plan(query)

print("\nPlan:")
print(plan)


print("\n==============================")
print("EXECUTING PLAN")
print("==============================")


results = execute_plan(plan)

print("\nTool Results:")
print(results)