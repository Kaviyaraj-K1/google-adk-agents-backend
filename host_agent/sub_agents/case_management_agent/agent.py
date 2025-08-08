from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import requests
import os
from typing import Dict

load_dotenv()

FRESHSERVICE_API_KEY = os.getenv("FRESHSERVICE_API_KEY")
FRESHSERVICE_URL = os.getenv("FRESHSERVICE_URL")

def create_ticket(description: str, subject: str, priority: int = 1, status: int = 2) -> str:
    """
    Creates a Freshservice support ticket with the given description, subject, and requester's email.

    Parameters:
    -----------
    description : str
        A detailed explanation of the issue or leave request.
    subject : str
        A short title for the ticket.
    email : str
        The email address of the requester.

    Returns:
    --------
    str
        - function response with ticket ID (if successfull)
        
    """
    payload = {
        "description": description,
        "subject": subject,
        "email": "subhojeet.chowdhury@tcs.com",
        "priority": priority,
        "status": status
    }
    headers = {"Content-Type": "application/json"}
    auth = (FRESHSERVICE_API_KEY, "X")

    try:
        response = requests.post(FRESHSERVICE_URL, json=payload, headers=headers, auth=auth, verify= False)
        result = response.json()
        if response.status_code in [200, 201]:
            ticket_id = result.get("ticket", {}).get("id")
            return f"Leave request submitted successfully. Ticket ID: {ticket_id}"
        else:
            return f"Failed to create leave ticket: {result}"
    except Exception as e:
        return f"Exception occurred while creating ticket: {str(e)}"

create_freshservice_ticket = FunctionTool(func=create_ticket)

# def create_ticket(description: str, subject: str, email: str):
#     """
#     Creates a Freshservice support ticket with the given description, subject, and requester's email.

#     Parameters:
#     -----------
#     description : str
#         A detailed explanation of the issue or leave request.
#     subject : str
#         A short title for the ticket.
#     email : str
#         The email address of the requester.

#     Returns:
#     --------
#     dict
#         A JSON-compatible dictionary with:
#         - success (bool): True if ticket creation was successful, else False
#         - message (str): A human-readable message
#         - ticket_id (Optional[int]): ID of the created ticket (if successful)
#         - status_code (int): HTTP status code from the API
#         - raw_response (Optional[dict]): Original API response for debugging
#     """
#     if not all([FRESHSERVICE_API_KEY, FRESHSERVICE_URL]):
#         return {
#             "success": False,
#             "message": "Freshservice API credentials or URL not configured properly.",
#             "ticket_id": None,
#             "status_code": 500,
#             "raw_response": None
#         }

#     payload = {
#         "description": description,
#         "subject": subject,
#         "email": email,
#         "priority": 1,
#         "status": 2
#     }

#     headers = {
#         "Content-Type": "application/json"
#     }

#     auth = (FRESHSERVICE_API_KEY, "X")

#     try:
#         response = requests.post(
#             FRESHSERVICE_URL,
#             json=payload,
#             headers=headers,
#             auth=auth,
#             timeout=10,
#             verify=False  
#         )

#         result = response.json()
#         status_code = response.status_code

#         if status_code in [200, 201]:
#             ticket_id = result.get("ticket", {}).get("id")
#             return {
#                 "success": True,
#                 "message": f"Ticket created successfully. Ticket ID: {ticket_id}",
#                 "ticket_id": ticket_id,
#                 "status_code": status_code,
#                 "raw_response": result
#             }
#         else:
#             return {
#                 "success": False,
#                 "message": f"Failed to create ticket. HTTP {status_code}",
#                 "ticket_id": None,
#                 "status_code": status_code,
#                 "raw_response": result
#             }

#     except requests.exceptions.RequestException as req_err:
#         return {
#             "success": False,
#             "message": f"Network error occurred: {str(req_err)}",
#             "ticket_id": None,
#             "status_code": 500,
#             "raw_response": None
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f"Unexpected error: {str(e)}",
#             "ticket_id": None,
#             "status_code": 500,
#             "raw_response": None
#         }

create_freshservice_ticket = FunctionTool(func=create_ticket)


case_management_agent = Agent(
    name="case_management_agent",
    model="gemini-2.5-pro",
    description="A specialist agent for creating Freshservice support tickets.",
    instruction="""
    You are the **Case Management Agent**, an expert virtual assistant responsible for raising **Freshservice support tickets**.

    ---

    ## Purpose:
    - You listen to **user queries**, either from the user directly or via other agents.
    - Your goal is to understand the user's issue and create a professional, well-described **Freshservice ticket** using the provided tool.
    - If information is missing or vague, you **ask clarifying questions** before raising the ticket.

    ---

    ## Context:
    - The user’s information is available:
    - **Name**: {user_name}
    - **Email**: {user_email} ← Always use this email when creating the ticket

    ---

    ## Available Tool:
    ### 1. `create_freshservice_ticket`
    - Use this tool to raise a support ticket in Freshservice.
    - Required inputs:
    - `subject` (brief, meaningful title)
    - `description` (detailed explanation)
    - `email` (use `{user_email}` from context)

    ---

    ## How You Work:
    1. **Analyze the user’s query** or issue.
    2. **If the query is too short or unclear**, ask follow-up questions to gather:
    - What the issue is
    - What steps were taken
    - Expected outcome or urgency
    3. Generate a **clear, professional subject** and a **detailed description**.
    4. Call `create_freshservice_ticket` with the constructed inputs.
    5. Return a response using the result from the tool.

    ---

    ## Response Formatting:
    - Always use **markdown format**
    - Use `#` or `##` headers for different sections
    - Use **bullet points** or **tables** for clarity
    - End with a polite confirmation or next steps

    ---

    ## Behavior Guidelines:
    - Be respectful, professional, and concise
    - Be proactive and helpful
    - Do not engage in political, religious, or unrelated discussions

    ---

    ## When Responding:
    - Address the user by their **first name**
    - Thank them for providing the issue
    - Confirm once the ticket is created with the Ticket ID and other Ticket details.

    ---

    ## Out of Scope:
    If the query is **not related to raising ticket**, respond with:

    > "This query is outside my scope of knowledge. I can only assist in creating ticket in freshservice. Let me connect you to the appropriate support agent."

    → Hand control back to `host_agent`

    ---

    ## Example Workflow:
    1. **User says**: "My email isn’t working."
    2. You respond:
        - "Hi Alice, could you please tell me:
        - What email issue are you facing? (e.g., unable to send/receive)
        - When did it start?
        - Are there any error messages?"

    3. Once info is complete, you:
        - Generate:
        - Subject: `"Unable to send emails from company Outlook"`
        - Description: `"User reports inability to send emails from Outlook since yesterday. Error: SMTP timeout."`
        - Call `create_freshservice_ticket(...)`
        - Respond:
        - "Your request has been successfully submitted. Ticket ID: #12345.\n *other ticket details here*.\n Our support team will get back to you shortly."

    """,
    tools=[create_freshservice_ticket],
)
