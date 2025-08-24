# Import necessary libraries
import os
import regex
import sys
import json
import base64
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Generator
from dotenv import load_dotenv
from logger_config import setup_logger
from utils import call_agent_query_async, create_session, retrieve_session, create_runner
from google.adk.sessions import InMemorySessionService

# Importing the agents
from agents import Base

# Load the .env file
load_dotenv()

# Default User
APP_NAME = os.getenv("APP_NAME")
USER_ID = "user_1"
SESSION_ID = "session_001"

# Configure logging
logging = setup_logger("orion_logs")

# Session configuration
session_service_memory = InMemorySessionService()

session_service = session_service_memory

# ------------------ Global runner ------------------
runner = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------------------ Initialize session and runner ------------------
    global runner
    session = await retrieve_session(
        session_service=session_service,
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        logging=logging
    )

    if not session:
        session = await create_session(
            session_service=session_service,
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
            logging=logging,
            state={
            "problem_config":   {    
                # Core content details
                "post_type": None,            # e.g., 'impact_story', 'blog', 'flyer', 'social_awareness', 'etc'
                "title": None,                # Optional title for post
                "summary": None,              # Short summary or description
                "keywords": None,             # List of relevant keywords or hashtags
                
                # Content format & style
                "tone": "motivational",                 # e.g., 'formal', 'casual', 'emotional', 'motivational'
                "length": "medium",               # e.g., 'short', 'medium', 'long'
                "language": "english",             # Default language
                "style": None,

                # Media & references
                "external_reference_links": None,       # URLs for references or sources
                "hashtags": None,

                # Target & audience
                "target_audience": None,      # e.g., 'students', 'general public', 'environment activists'
                
                # Optional constraints
                "special_requirements": None  # e.g., 'include statistics', 'cite sources', 'focus on local region'
            },
            "generated_post": None,
            "final_image": None,
            "final_post": None,
            "web_info_output": None, 
        }
    )

    runner = await create_runner(
        agent=Base,
        app_name=APP_NAME,
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

    # Request body model
class PromptRequest(BaseModel):
    prompt: str


@app.post("/agent/query")
async def agent_query(request: PromptRequest):
    try:
        response = await call_agent_query_async(
            query=request.prompt,
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID,
            logging=logging
        )
        match = regex.search(r'```(?:JSON)?\s*(\{.*?\})\s*```', response, regex.DOTALL | regex.IGNORECASE)

        if not match:
            # Fallback: match any standalone JSON object including nested braces
            match = regex.search(r'(\{(?:[^{}]|(?0))*\})', response, regex.DOTALL)
        
        if match:
            json_str = match.group(1)
            json_str = json_str.replace("True", "true").replace("False", "false").replace("None", "null")
            data = json.loads(json_str)

            # 🔹 If generated_image is True, read image and return binary (base64)
            if data.get("generated_image") is True:
                try:
                    with open(r"C:\Users\lenovo\OneDrive\Desktop\Skillcred\Impact AI\Agentic\output\generated_image.png", "rb") as f:
                        image_bytes = f.read()
                        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
                    
                    return {
                        "status": "success",
                        "image_base64": image_b64
                    }
                except FileNotFoundError:
                    raise HTTPException(status_code=404, detail="Image file not found")
            else:
                # Handle the case when image generation failed or is not present
                raise HTTPException(status_code=400, detail="Image was not generated")       
        return {"status": "success", "response": response}
    except Exception as e:
        logging.error(f"Agent query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)