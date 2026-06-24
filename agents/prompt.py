from pydantic import BaseModel, Field
from typing import List


# Pydantic models for structured output
class JiraWorkLog(BaseModel):
    ticket_id: str = Field(default = "UNCATEGORIZED", description = "The Jira ticket identifier found in the commit or text (e.g., PROJ-123, DEV-45).")
    time_spent: str = Field(default = "30m", description = "The calculated time spent in Jira format (e.g., '30m', '1h', '2h 30m'). Default to '30m' per commit if unknown.")
    comment: str = Field(default = "Code updates and development.", description = "A professional, consolidated summary of the work done for this ticket. Combine multiple commits into one clean bulleted list if necessary.")


class WorkLogExtraction(BaseModel):
    """
        The format that Gemini must return
    """
    worklogs: List[JiraWorkLog]


# The core system prompt
# Leave your Pydantic classes exactly as they are. Just update the prompt string:

SYSTEM_PROMPT = """You are an elite Engineering Manager Assistant. Your job is to take a developer's raw daily GitHub commits and manual notes, and format them into a professional Jira worklog for a specific, provided ticket.

INSTRUCTIONS:
1. You will be provided with a `Target Ticket ID`, `Manual Notes`, and raw `Commits`.
2. Group the commits and notes into a single worklog entry.
3. Write a professional `comment` summarizing the work. Translate messy logs into polished business language.
4. Calculate `time_spent`. If not specified in the manual notes, default to '30m' per commit.

CRITICAL RULES FOR OUTPUT CLEANLINESS:
- Assign the worklog to the EXACT `Target Ticket ID` provided in the input payload.
- Do not invent fake ticket IDs.
- Double check that you spell the fields exactly as: `ticket_id`, `time_spent`, and `comment`.
"""
