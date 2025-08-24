from google.adk.tools import FunctionTool, ToolContext

def exit_loop(tool_context: ToolContext):
    """Signals that the iterative process should end."""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    # This is the key action that tells the LoopAgent to stop
    tool_context.actions.escalate = True
    return {}