import asyncio
import uuid
from fastapi.responses import StreamingResponse
import json
import time
import hashlib
import os
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

# Import the main customer service agent
from host_agent.agent import host_agent
from utils import add_user_query_to_history, call_agent_async,process_agent_response_streaming
from session_store import AuthSessionStore

load_dotenv()

# Using SQLite database for persistent storage
db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# ===== PART 1: User Management =====
# Simple in-memory user store (in production, use a proper database)
USERS_DB = {
    "demo@company.com": {
        "password_hash": hashlib.sha256("demo123".encode()).hexdigest(),
        "user_name": "Demo User",
        "user_email": "demo@company.com",
        "role": "employee"
    },
    "admin@company.com": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "user_name": "Admin User",
        "user_email": "admin@company.com",
        "role": "admin"
    },
    "subhojeet.chowdhury.work@gmail.com": {
        "password_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "user_name": "Subhojeet Chowdhury",
        "user_email": "subhojeet.chowdhury.work@gmail.com",
        "role": "employee"
    }
}

# Active sessions store (SQLite)
auth_store = AuthSessionStore(db_path="auth_sessions.db")

# ===== PART 2: App Config =====
APP_NAME = "AESS"

# ===== PART 3: Setup Runner =====
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

# ===== PART 4: Request Models =====
class QueryRequest(BaseModel):
    query: str

class LoginRequest(BaseModel):
    email: str
    password: str
    remember: bool = False

class LogoutRequest(BaseModel):
    session_id: str

# ===== PART 5: Authentication Functions =====
def authenticate_user(email: str, password: str):
    """Authenticate user with email and password"""
    if email not in USERS_DB:
        return None
    
    user = USERS_DB[email]
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if user["password_hash"] == password_hash:
        return user
    return None

def create_user_session(user: dict):
    """Create a new session for authenticated user"""
    session_id = str(uuid.uuid4())
    
    # Create initial state for the user
    initial_state = {
        "user_name": user["user_name"],
        "user_email": user["user_email"],
        "user_role": user["role"],
        "interaction_history": [],
        "login_time": datetime.now().isoformat(),
    }
    
    # Auth session persistence happens after backend session creation
    return session_id, initial_state

async def create_backend_session(user_id: str, session_id: str, initial_state: dict):
    """Create session in the backend session service"""
    try:
        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state=initial_state,
        )
        print(f"New session created id: {session_id}")
        return new_session
    except Exception as e:
        print(f"Error creating backend session: {e}")
        return None

# ===== PART 6: API Endpoints =====
@app.post("/login")
async def login(request: LoginRequest):
    """Authenticate user and create session"""
    try:
        # Authenticate user
        user = authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create session
        session_id, initial_state = create_user_session(user)
        
        # Create backend session
        backend_session = await create_backend_session(
            user_id=user["user_email"],
            session_id=session_id,
            initial_state=initial_state
        )
        
        if not backend_session:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        # Persist active session in SQLite
        auth_store.create_session(
            session_id=session_id,
            user_email=user["user_email"],
            user_name=user["user_name"],
            role=user["role"],
        )
        
        return {
            "success": True,
            "user_name": user["user_name"],
            "user_email": user["user_email"],
            "session_id": session_id,
            "message": "Login successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/logout")
async def logout(request: LogoutRequest):
    """Logout user and clear session"""
    try:
        session_id = request.session_id
        
        # Remove from active sessions (SQLite)
        auth_store.delete(session_id)
        
        return {"success": True, "message": "Logout successful"}
        
    except Exception as e:
        print(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    session_info = auth_store.get_session(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_info["session_id"],
        "user": {
            "user_email": session_info["user_email"],
            "user_name": session_info["user_name"],
            "role": session_info.get("role"),
        },
        "created_at": session_info["created_at"],
        "last_activity": session_info["last_activity"],
    }

@app.post("/query")
async def process_query(req: QueryRequest, session_id: str = None):
    """Accepts user query, processes via agent, returns progress + response."""
    if not session_id:
        raise HTTPException(status_code=401, detail="Session ID required")
    
    session_info = auth_store.get_session(session_id)
    if not session_info:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Update last activity
    auth_store.touch(session_id)
    
    query_id = str(uuid.uuid4())
    user_input = req.query.strip()
    
    if not user_input:
        return {"error": "Query cannot be empty"}

    user_email = session_info["user_email"]

    await add_user_query_to_history(session_service, APP_NAME, user_email, session_id, user_input)

    result = await call_agent_async(runner, user_email, session_id, user_input)

    return {
        "query_id": query_id,
        "user": user_email,
        "query": user_input,
        "progress": result["progress"], 
        "response": result["response"] or "[No response generated]",
    }

@app.get("/query-streaming")
async def query_streaming(query: str, session_id: str = None):
    """Streams progress updates live using SSE."""
    if not session_id:
        raise HTTPException(status_code=401, detail="Session ID required")
    
    session_info = auth_store.get_session(session_id)
    if not session_info:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Update last activity
    auth_store.touch(session_id)
    
    query_id = str(uuid.uuid4())

    async def event_generator():
        user_email = session_info["user_email"]
        
        # Save query in session
        await add_user_query_to_history(session_service, APP_NAME, user_email, session_id, query)

        yield f"data: {json.dumps({'query_id': query_id})}\n\n"

        content = types.Content(role="user", parts=[types.Part(text=query)])
        agent_name = None

        try:
            async for event in runner.run_async(user_id=user_email, session_id=session_id, new_message=content):
                # Agent start
                if event.author and agent_name is None:
                    agent_name = event.author

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
async def get_current_state(session_id: str = None):
    """Debug endpoint to check session state."""
    if not session_id:
        raise HTTPException(status_code=401, detail="Session ID required")
    
    session_info = auth_store.get_session(session_id)
    if not session_info:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    try:
        user_email = session_info["user_email"]
        
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_email, session_id=session_id
        )
        return session.state
    except Exception as e:
        print(f"Error getting state: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving session state")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
