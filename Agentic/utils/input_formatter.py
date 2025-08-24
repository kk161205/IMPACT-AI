from google.genai import types

def format_query(query: str) -> types.Content:
    """ Formats a user query into a structured content type. """
    return types.Content(role='user', parts=[types.Part(text=query)])