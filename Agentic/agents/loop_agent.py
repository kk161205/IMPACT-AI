from google.adk.agents import LoopAgent, LlmAgent
# Assuming the other agents are defined in 'agents.py'
from agents import Refine_agent, Refactor_agent

Refinement_Loop_Agent = LoopAgent(
    name="Refinement_Loop_Agent",
    description=(
        "An agent that iteratively refines and refactors generated text, exiting early if the text is polished."
    ),
    # The order of sub-agents is crucial here: Refine first, then Refactor
    sub_agents=[Refine_agent, Refactor_agent],
    # A safety net to prevent infinite loops
    max_iterations=5,
)