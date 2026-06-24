from pydantic import BaseModel, Field
from typing import List


# Pydantic models for structured output
class JiraWorkLog(BaseModel):
    ticked_id: str = Field(description = "The Jira ticket identifier found in the commit or text (e.g., PROJ-123, DEV-45).")
    time_spent: str = Field(description = "The calculated time spent in Jira format (e.g., '30m', '1h', '2h 30m'). Default to '30m' per commit if unknown.")
    comment: str = Field(description = "A professional, consolidated summary of the work done for this ticket. Combine multiple commits into one clean bulleted list if necessary.")


class WorkLogExtraction(BaseModel):
    """
        The format that Gemini must return
    """
    worklogs: List[JiraWorkLog]


# The core system prompt
SYSTEM_PROMPT = """You are an elite Engineering Manager Assistant. Your job is to take a developer's raw daily GitHub commits and their manual text notes, and convert them into professional, ready-to-log Jira worklogs.

INSTRUCTIONS:
1. Analyze the provided manual user notes and the raw GitHub commit logs.
2. Identify any Jira ticket keys (e.g., "CORE-112", "APP-99") mentioned in branch names, commit messages, or manual text.
3. Group all commits and notes belonging to the same Jira ticket together.
4. Write a professional `comment` summarizing the work. Translate messy developer commits (e.g., "fixed typo", "wip auth") into polished business language (e.g., "Resolved authentication edge case and refactored login flow").
5. Calculate `time_spent`. If the manual text specifies time for a task, use that. Otherwise, estimate roughly 30 minutes ('30m') to 1 hour ('1h') per substantial commit.

RULES:
- DO NOT invent ticket IDs. If a commit has no recognizable ticket ID, group it under a generic "N/A" ticket, or skip it based on the user's manual text.
- Output ONLY the requested data structure. No conversational filler.
"""
