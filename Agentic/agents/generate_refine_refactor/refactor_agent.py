from google.adk.agents import LlmAgent
from tools import exit_loop
from google.adk.tools import FunctionTool

Refactor_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="Refactor_agent",
    description=(
        "Refines generated text using refinement suggestions or exits the loop if the text is polished."
    ),
    instruction=(
        "1. Read the text from {generated_post} and the suggestions from {refinement_suggestions}.\n"
        "2. If {refinement_suggestions} is 'refinement_complete', call the `exit_loop` tool to terminate.\n"
        "3. Apply ONLY the refinement suggestions to rewrite the text, preserving the original meaning.\n"
        "   - For tone, grammar, or structure, follow the suggestions directly.\n"
        "   - Do not make changes outside the suggestions.\n"
        "   - Do not add ```text ```.\n"
        "4. Conflict Handling:\n"
        "   - Prioritize clarity and readability over style or tone.\n"
        "5. Edge Case Handling:\n"
        "   - Ignore impossible suggestions.\n"
        "   - If {refinement_suggestions} is empty, return {generated_post} unchanged.\n"
        "6. Return ONLY the final refined text in {generated_post}, no explanations or metadata."
    ),
    tools=[FunctionTool(func=exit_loop)],
    output_key="generated_post"
)
