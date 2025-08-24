from google.adk.agents import SequentialAgent
from agents import Text_generator
from agents import Refinement_Loop_Agent

Orchestrator_Agent = SequentialAgent(
    name="Orchestrator_Agent",
    description=(
        "Generates a complete text and then refines it through an iterative loop. "
        "Passes {problem_config} and {web_info_output} to sub-agents for controlled refinement."
    ),
    sub_agents=[Text_generator, Refinement_Loop_Agent]
)
