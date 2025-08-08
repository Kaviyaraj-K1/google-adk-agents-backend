import asyncio
import uuid
from fastapi.responses import StreamingResponse
import json
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

# Import the main customer service agent
from host_agent.agent import host_agent
from utils import add_user_query_to_history, call_agent_async,process_agent_response_streaming

load_dotenv()

# Using SQLite database for persistent storage
db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)


# ===== PART 1: Initialize In-Memory Session Service =====
# session_service = InMemorySessionService()

# ===== PART 2: Define Initial State =====
initial_state = {
    "user_name": "subhojeet chowdhury",
    "user_email": "subhojeet.chowdhury.work@gmail.com",
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

    # # Check for existing sessions for this user
    # existing_sessions = await session_service.list_sessions(
    #     app_name=APP_NAME,
    #     user_id=USER_ID,
    # )

    # # If there's an existing session, use it, otherwise create a new one
    # if existing_sessions and len(existing_sessions.sessions) > 0:
    #     # Use the most recent session
    #     SESSION_ID = existing_sessions.sessions[0].id
    #     print(f"Continuing existing session: {SESSION_ID}")
    # else:
    #     # Create a new session with initial state
    #     new_session = await session_service.create_session(
    #         app_name=APP_NAME,
    #         user_id=USER_ID,
    #         state=initial_state,
    #     )
    #     SESSION_ID = new_session.id
    #     print(f"✅ Created new session: {SESSION_ID}")


    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    print(f"✅ Created new session: {SESSION_ID}")


class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def process_query(req: QueryRequest):
    """Accepts user query, processes via agent, returns progress + response."""
    query_id = str(uuid.uuid4())
    user_input = req.query.strip()
    
    if not user_input:
        return {"error": "Query cannot be empty"}

    await add_user_query_to_history(session_service, APP_NAME, USER_ID, SESSION_ID, user_input)

    result = await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

    return {
        "query_id": query_id,
        "user": USER_ID,
        "query": user_input,
        "progress": result["progress"], 
        "response": result["response"] or "[No response generated]",
    }

@app.get("/query-streaming")
async def query_streaming(query: str):
    """Streams progress updates live using SSE."""
    query_id = str(uuid.uuid4())

    async def event_generator():
        # Save query in session
        await add_user_query_to_history(session_service, APP_NAME, USER_ID, SESSION_ID, query)

        yield f"data: {json.dumps({'query_id': query_id})}\n\n"

        content = types.Content(role="user", parts=[types.Part(text=query)])
        agent_name = None

        try:
            async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
                # Agent start
                if event.author and agent_name is None:
                    agent_name = event.author
                    # yield f"data: {json.dumps({'progress': f'🤖 Agent {agent_name} is now handling your request.'})}\n\n"

                # Stream progress in real time
                async for msg in process_agent_response_streaming(event):

                    time.sleep(1)
                    yield f"data: {json.dumps({'progress': msg})}\n\n"

                # Final response
                if event.is_final_response():
                    final_response = None
                    if event.content and event.content.parts:
                        text_parts = [p.text for p in event.content.parts if hasattr(p, "text") and p.text]
                        if text_parts:
                            final_response = "\n".join(text_parts)
                    if final_response:
                        time.sleep(2)
                        yield f"data: {json.dumps({'final_response': final_response})}\n\n"

            yield "event: end\ndata: {}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/state")
async def get_current_state():
    """Debug endpoint to check session state."""
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    return session.state
