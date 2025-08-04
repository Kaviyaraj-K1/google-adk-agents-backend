import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import the main customer service agent
from host_agent.agent import host_agent
from utils import add_user_query_to_history, call_agent_async

load_dotenv()

# ===== PART 1: Initialize In-Memory Session Service =====
session_service = InMemorySessionService()

# ===== PART 2: Define Initial State =====
initial_state = {
    "user_name": "subhojeet chowdhury",
    "interaction_history": [],
}

# ===== PART 3: App Config =====
APP_NAME = "AESS"
USER_ID = "subhojeet"
SESSION_ID = None  # will be initialized at startup

# ===== PART 4: Setup Runner =====
runner = Runner(
    agent=host_agent,
    app_name=APP_NAME,
    session_service=session_service,
)

# ===== FastAPI Setup =====
app = FastAPI(title="AESS Agent API")

# Add CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000", "http://localhost:5000"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Create session when FastAPI starts"""
    global SESSION_ID
    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    print(f"✅ Created new session: {SESSION_ID}")


class QueryRequest(BaseModel):
    query: str


# @app.post("/query")
# async def process_query(req: QueryRequest):
#     """Accepts user query, processes via agent, returns response."""
#     user_input = req.query.strip()

#     if not user_input:
#         return {"error": "Query cannot be empty"}

#     # Add user query to history
#     await add_user_query_to_history(
#         session_service, APP_NAME, USER_ID, SESSION_ID, user_input
#     )

#     # Process query using agent
#     final_response = await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

#     return {
#         "user": USER_ID,
#         "query": user_input,
#         "response": final_response or "[No response generated]",
#     }

@app.post("/query")
async def process_query(req: QueryRequest):
    """Accepts user query, processes via agent, returns progress + response."""
    user_input = req.query.strip()
    if not user_input:
        return {"error": "Query cannot be empty"}

    await add_user_query_to_history(session_service, APP_NAME, USER_ID, SESSION_ID, user_input)

    result = await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

    return {
        "user": USER_ID,
        "query": user_input,
        "progress": result["progress"],  # Ordered progress
        "response": result["response"] or "[No response generated]",
    }



@app.get("/state")
async def get_current_state():
    """Debug endpoint to check session state."""
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    return session.state
