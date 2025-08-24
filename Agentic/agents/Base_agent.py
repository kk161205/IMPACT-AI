from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from agents.requirement_gatherer_agent import Requirement_gatherer
from agents.web_info_agent import Web_info
from agents.improvement import Orchestrator_Agent
from agents.image_agent import image_generation_agent

# Wrap tools
web_info_tool = AgentTool(Web_info)
image_tool = AgentTool(image_generation_agent)

Base = LlmAgent(
    name="Base_agent",
    model="gemini-2.5-flash",
    description=(
        "Root agent that coordinates requirement gathering, optional web info retrieval, "
        "text and image content generation, and refinement to produce the final polished content."
    ),
    instruction=(
        "1. Check the user's query. If the user is not explicitly asking to generate a post or visual content, "
        "have a normal conversation. Answer questions, explain your capabilities, or provide general assistance. "
        "Do not start any post generation steps.\n\n"

        "2. If the user explicitly asks in their query to generate a post or visual content, start the post generation workflow as needed:\n\n"

        "   a. Call the `Requirement_gatherer`, to gather post details from the user.\n\n"

        "   b. Call the `web_info_tool` only if external info is required or if the user explicitly asks for external information.\n\n"

        "   c. Determine the `post_type` from {problem_config}.\n\n"

        "   d. Call the `Orchestrator_Agent` to generate/refine text if `post_type` includes text, "
        "and only if the user explicitly asked for a post in their query.\n\n"

        "   e. Call the `image_tool` to generate an image only if `post_type` indicates a visual post "
        "(e.g., flyer, poster, infographic), {final_image} is not yet set, and only if the user explicitly asked for a post in their query.\n\n"

        "   f. If the user updates any values in their query (e.g., changes the text, post_type, or other requirements), "
        "update the corresponding {problem_config}, {web_info_output}, {final_post}, or {final_image} values as needed "
        "without restarting the entire workflow.\n\n"

        "3. Return the final results: {final_post} for text, and if image is generated only send an object {'generated_image': True} only. "
        "Do not repeat any previous steps unnecessarily; only call each agent when its output is needed and matches the `post_type`, "
        "and only if the user explicitly requested post generation in their query."
    ),
    sub_agents=[
        Requirement_gatherer,
        Orchestrator_Agent,
        image_generation_agent
    ],
    tools=[web_info_tool, image_tool]
)
