from google.adk.agents import LlmAgent

# Mapping for length categories to word ranges
LENGTH_MAP = {
    "short": "250-350 words",
    "medium": "500-700 words",
    "long": "800-1000 words"
}

Text_generator = LlmAgent(
    model="gemini-2.5-flash",
    name="Text_generator",
    description=(
        "Generates a complete post (article, blog, short story, etc.) based on "
        "user requirements in 'problem_config' and optional supporting data in 'web_info_output'. "
        "Receives explicit context keys for controlled generation."
    ),
    instruction=(
        "1. Read all relevant fields from {problem_config}: 'post_type', 'title', 'summary', "
        "'tone', 'length', and 'target_audience'.\n"
        "2. Use {web_info_output} if it exists; otherwise, rely solely on problem_config to generate the text. "
        "The web data should only be used to enrich factual content.\n"
        "3. Map the 'length' field to word count using: short ~250-350, medium ~500-700, long ~800-1000.\n"
        "4. Respect 'tone' and 'target_audience' strictly.\n"
        "5. Format the post clearly with headings, paragraphs, and lists where appropriate.\n"
        "6. Return only the final text as a string under 'generated_post'. "
        "Do NOT add JSON, keys, or extra commentary. Do not add ```text ```.\n"
        "7. Ensure proper grammar, readability, and professional tone. The text should be polished and ready for publication."
    ),
    output_key="generated_post"
)
