import os
import sys
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from logger_config import setup_logger
from utils import call_agent_query_async, create_session, retrieve_session, create_runner, fetch_metadata
from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import InMemorySessionService
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Generator
import yaml
import json
from pathlib import Path

# Importing environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Importing the agents
from agents import RootAgent

# Default User ID and Session ID
USER_ID = "user_1"
SESSION_ID = "session_001"

# Configure logging
logging = setup_logger("fedex_bot")

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    logging.error("DB_URL environment variable is not set!")    
    sys.exit(1)

# Session configuration
session_service_db = DatabaseSessionService(db_url=os.getenv("DB_URL"))
session_service_memory = InMemorySessionService()

enable_db_session = os.getenv("ENABLE_DB_SESSION").lower() == "true"
session_service = session_service_db if enable_db_session else session_service_memory

if not os.getenv("AZURE_API_KEY"):
    logging.error("AZURE_API_KEY environment variable is not set!")    
    sys.exit(1)

if not os.getenv("AZURE_API_VERSION"):
    logging.error("AZURE_API_VERSION environment variable is not set!")  
    sys.exit(1)

if not os.getenv("AZURE_API_BASE"):
    logging.error("AZURE_API_BASE environment variable is not set!")  
    sys.exit(1)
    
if not os.getenv("AZURE_API_DEPLOYMENT"):
    logging.error("AZURE_API_DEPLOYMENT environment variable is not set!")  
    sys.exit(1)

# ------------------ Global runner ------------------
runner = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------------------ Initialize session and runner ------------------
    global runner
    session = await retrieve_session(
        session_service=session_service,
        app_name="ROOT_APP",
        user_id=USER_ID,
        session_id=SESSION_ID,
        logging=logging
    )

    if not session:
        session = await create_session(
            session_service=session_service,
            app_name="ROOT_APP",
            user_id=USER_ID,
            session_id=SESSION_ID,
            logging=logging
        )

    runner = await create_runner(
        agent=RootAgent,
        app_name="ROOT_APP",
        session_service=session_service,
        logging=logging
    )

    logging.info("Session and runner initialized successfully")

    try:
        yield  # the app runs here
    finally:
        # Optional: cleanup if needed
        logging.info("Lifespan ending, cleaning up resources...")

# Server configuration
app = FastAPI(lifespan=lifespan)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

###################################################################################
# Importing routes

# Home Route
@app.get("/")
async def root():
    return {"message": f"Server is running at port: {os.getenv("PORT", 8000)}!"}

def load_json_file(path: str) -> Any:
    """
    Load a standard JSON file and return the parsed object (dict / list).
    Raises ValueError on invalid JSON or FileNotFoundError if file missing.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    text = p.read_text(encoding="utf-8")
    return json.loads(text)

def load_jsonl_to_list(path: str) -> List[dict]:
    """
    Loads entire JSONL (one JSON object per line) into a Python list.
    Returns a list of parsed objects.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    results = []
    with p.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON on line {lineno}: {e}") from e
    return results

@app.post("/data-product")
async def generate_data_product(yaml_file: UploadFile = File(...), mapping_file: UploadFile = File(...)):
    yaml_config = yaml.safe_load(await yaml_file.read())
    mapping_json = json.loads(await mapping_file.read())
    
    # Step 1: fetch schema from Postgres
    # schema = fetch_metadata(yaml_config["source"]) 

    schema = load_jsonl_to_list("./utils/output.jsonl")

    prompt = f'''
        Source schema: {schema}
        Target columns + ETL tasks: {mapping_json}
        YAML File: {yaml_config}
    '''

    # Calling the agent with a query
    await call_agent_query_async(
        query=prompt,
        runner=runner,
        user_id=USER_ID,
        session_id=SESSION_ID,
        logging=logging
    )

    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)