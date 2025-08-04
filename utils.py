from datetime import datetime

from google.genai import types


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


async def update_interaction_history(session_service, app_name, user_id, session_id, entry):
    """Add an entry to the interaction history in state.

    Args:
        session_service: The session service instance
        app_name: The application name
        user_id: The user ID
        session_id: The session ID
        entry: A dictionary containing the interaction data
            - requires 'action' key (e.g., 'user_query', 'agent_response')
            - other keys are flexible depending on the action type
    """
    try:
        # Get current session
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        # Get current interaction history
        interaction_history = session.state.get("interaction_history", [])

        # Add timestamp if not already present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the entry to interaction history
        interaction_history.append(entry)

        # Create updated state
        updated_state = session.state.copy()
        updated_state["interaction_history"] = interaction_history

        # Create a new session with updated state
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=updated_state,
        )
    except Exception as e:
        print(f"Error updating interaction history: {e}")


async def add_user_query_to_history(session_service, app_name, user_id, session_id, query):
    """Add a user query to the interaction history."""
    await update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "user_query",
            "query": query,
        },
    )


async def add_agent_response_to_history(
    session_service, app_name, user_id, session_id, agent_name, response
):
    """Add an agent response to the interaction history."""
    await update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "agent_response",
            "agent": agent_name,
            "response": response,
        },
    )


async def display_state(
    session_service, app_name, user_id, session_id, label="Current State"
):
    """Display the current session state in a formatted way."""
    try:
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        # Format the output with clear sections
        print(f"\n{'-' * 10} {label} {'-' * 10}")

        # Handle the user name
        user_name = session.state.get("user_name", "Unknown")
        print(f"👤 User: {user_name}")

        # Handle purchased courses
        purchased_courses = session.state.get("purchased_courses", [])
        if purchased_courses and any(purchased_courses):
            print("📚 Courses:")
            for course in purchased_courses:
                if isinstance(course, dict):
                    course_id = course.get("id", "Unknown")
                    purchase_date = course.get("purchase_date", "Unknown date")
                    print(f"  - {course_id} (purchased on {purchase_date})")
                elif course:  # Handle string format for backward compatibility
                    print(f"  - {course}")
        else:
            print("📚 Courses: None")

        # Handle interaction history in a more readable way
        interaction_history = session.state.get("interaction_history", [])
        if interaction_history:
            print("📝 Interaction History:")
            for idx, interaction in enumerate(interaction_history, 1):
                # Pretty format dict entries, or just show strings
                if isinstance(interaction, dict):
                    action = interaction.get("action", "interaction")
                    timestamp = interaction.get("timestamp", "unknown time")

                    if action == "user_query":
                        query = interaction.get("query", "")
                        print(f'  {idx}. User query at {timestamp}: "{query}"')
                    elif action == "agent_response":
                        agent = interaction.get("agent", "unknown")
                        response = interaction.get("response", "")
                        # Truncate very long responses for display
                        if len(response) > 100:
                            response = response[:97] + "..."
                        print(f'  {idx}. {agent} response at {timestamp}: "{response}"')
                    else:
                        details = ", ".join(
                            f"{k}: {v}"
                            for k, v in interaction.items()
                            if k not in ["action", "timestamp"]
                        )
                        print(
                            f"  {idx}. {action} at {timestamp}"
                            + (f" ({details})" if details else "")
                        )
                else:
                    print(f"  {idx}. {interaction}")
        else:
            print("📝 Interaction History: None")

        # Show any additional state keys that might exist
        other_keys = [
            k
            for k in session.state.keys()
            if k not in ["user_name", "purchased_courses", "interaction_history"]
        ]
        if other_keys:
            print("🔑 Additional State:")
            for key in other_keys:
                print(f"  {key}: {session.state[key]}")

        print("-" * (22 + len(label)))
    except Exception as e:
        print(f"Error displaying state: {e}")

async def process_agent_response(event):
    """Process agent events, log details, and create ordered progress updates."""
    print(f"Event ID: {event.id}, Author: {event.author}")

    progress_updates = []  # Collect progress messages for frontend

    # === Agent Delegation Progress ===
    if event.author:
        msg = f"🤖 Agent **{event.author}** is now handling your request."
        progress_updates.append(msg)

    # === Inspect Event Content ===
    if event.content and event.content.parts:
        for part in event.content.parts:
            # Handle text parts (logs + existing behavior)
            if hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  Text: '{part.text.strip()}'")

            # Handle function_call parts safely
            if hasattr(part, "function_call") and part.function_call:
                tool_name = getattr(part.function_call, "name", "UnknownTool")
                tool_args = getattr(part.function_call, "args", {})
                msg = f"🔧 Tool **{tool_name}** is being used."
                progress_updates.append(msg)
                print(f"[DEBUG] Tool Invoked: {tool_name} with args {tool_args}")

            # Handle function_response
            if hasattr(part, "function_response") and part.function_response:
                msg = f"✅ Tool execution completed."
                progress_updates.append(msg)
                print(f"[DEBUG] Tool Response: {part.function_response}")

    # === Final Response Handling ===
    final_response = None
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Existing pretty logging
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ AGENT RESPONSE ═════════════════════════════════════════{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═════════════════════════════════════════════════════════════{Colors.RESET}\n"
            )
        else:
            print(
                f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}==> Final Agent Response: [No text content]{Colors.RESET}\n"
            )

    return progress_updates, final_response


async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously, collect ordered progress updates + final response."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    final_response_text = None
    agent_name = None
    all_progress = []  # Keeps ordered progress

    await display_state(runner.session_service, runner.app_name, user_id, session_id, "State BEFORE processing")

    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.author:
                agent_name = event.author

            progress_updates, response = await process_agent_response(event)
            if progress_updates:
                all_progress.extend(progress_updates)  # Append in event order
            if response:
                final_response_text = response
    except Exception as e:
        all_progress.append("⚠ Error occurred while processing request.")
        print(f"{Colors.BG_RED}{Colors.WHITE}ERROR: {e}{Colors.RESET}")

    if final_response_text and agent_name:
        await add_agent_response_to_history(runner.session_service, runner.app_name, user_id, session_id, agent_name, final_response_text)

    await display_state(runner.session_service, runner.app_name, user_id, session_id, "State AFTER processing")

    return {"progress": all_progress, "response": final_response_text}
