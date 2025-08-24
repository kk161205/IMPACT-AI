from .input_formatter import format_query
from google.adk.runners import Runner
import logging

async def call_agent_query_async(query: str, runner: Runner, user_id: str, session_id: str, logging: logging.Logger) -> None:
    """
    Call the agent asynchronously with the provided query.

    Args:
        query (str): The user query to send to the agent.
        runner (Runner): The runner instance that manages the agent.
        user_id (str): The ID of the user making the request.
        session_id (str): The ID of the session for this interaction.

    Returns:
        str: The response from the agent.
    """

    logging.info(f"\n>>> User Query: {query}")

    content = format_query(query)

    final_response_text = "Agent did not produce a final response."
    
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        logging.info(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate: 
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    logging.info(f"\n<<< Agent Response: {final_response_text}")
    return final_response_text

async def create_session(session_service, app_name: str, user_id: str, session_id: str, state: dict, logging: logging.Logger):
    """ Create a new session for the agent. """
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=state
    )
    logging.info(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
    return session

async def retrieve_session(session_service, app_name: str, user_id: str, session_id: str, logging: logging.Logger):
    """ Retrieve an existing session for the agent. """
    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    logging.info(f"Session retrieved: App='{app_name}', User='{user_id}', Session='{session_id}'")
    return session

async def create_runner(agent, app_name: str, session_service, logging: logging.Logger) -> Runner:
    """ Create a runner for the agent. """
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )
    logging.info(f"Runner created for agent '{runner.agent.name}'.")
    return runner