from typing import Any, Dict, Union
from google.adk.tools import ToolContext

# Define which fields are expected to be lists
LIST_FIELDS = {"keywords", "hashtags", "external_reference_links"}

def update_problem_config_tool(
    key: str,
    value: Any,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Updates the session's problem_config state with a new value for the given key.
    Handles type validation for lists and strings, supports overwriting for dynamic updates.
    """
    if "problem_config" not in tool_context.state:
        return {
            "status": "error",
            "message": "Problem config has not been initialized in state.",
            "updated_config": None
        }

    problem_config = tool_context.state["problem_config"]

    if key not in problem_config:
        return {
            "status": "error",
            "message": f"Key '{key}' is not a valid problem_config field.",
            "updated_config": problem_config
        }

    previous_value = problem_config.get(key)

    # Type validation and coercion
    if key in LIST_FIELDS:
        if isinstance(value, str):
            # Convert comma-separated string to list
            value = [v.strip() for v in value.split(",") if v.strip()]
        elif not isinstance(value, list):
            return {
                "status": "error",
                "message": f"Invalid type for '{key}': expected list or comma-separated string.",
                "updated_config": problem_config
            }
    else:
        # Coerce to string for non-list fields
        value = str(value)

    # Update the key (overwrite if exists)
    problem_config[key] = value
    tool_context.state["problem_config"] = problem_config

    return {
        "status": "success",
        "message": f"Updated '{key}' from '{previous_value}' to '{value}'",
        "updated_config": problem_config
    }
