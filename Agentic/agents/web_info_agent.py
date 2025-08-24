from google.adk.agents import LlmAgent
from google.adk.tools import google_search

Web_info = LlmAgent(
    model="gemini-2.5-flash",
    name="Web_info",
    description=(
        "An agent that performs targeted web searches to gather supporting facts, links, "
        "and relevant data for content generation without exceeding quota limits."
    ),
    instruction=(
        "1. Use ONLY the 'title' and 'summary' from {problem_config} to form concise search queries.\n"
        "2. Perform searches using the `google_search` tool, limiting results to the top 5 most relevant links.\n"
        "3. Collect only the essential facts, statistics, and links, keeping the output concise and relevant.\n"
        "4. Store the final collected content in {web_info_output}.\n"
        "5. Return {web_info_output} as a single string suitable for content generation.\n"
        "6. Avoid repeating searches for the same query in the same session if possible."
    ),
    tools=[google_search]
)
