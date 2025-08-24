from google.adk.agents import LlmAgent

Refine_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="Refine_agent",
    description=(
        "Analyzes generated text and provides refinement suggestions, or signals completion. "
        "Receives context from {problem_config} for requirement-aware refinement."
    ),
    instruction=(
        "1. Read the text from {generated_post} in the state.\n"
        "2. Analyze the text for any remaining grammar issues, clarity problems, poor flow, or mismatches with {problem_config} requirements.\n"
        "3. If the text is clear, grammatically correct, and aligns with requirements, respond EXACTLY with 'refinement_complete'.\n"
        "4. If improvements are needed, return a numbered list of the top 3 most impactful, concise, and actionable suggestions.\n"
        "5. Suggest appropriate markdowns for better visuals.\n"
        "6. Do NOT modify the content — only return the phrase 'refinement_complete' OR a list of actionable refinement suggestions.\n"
        "7. Do not add ```text ```."
        
    ),
    output_key="refinement_suggestions"
)
