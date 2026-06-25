import os
from utils.logger import get_logger
from tools.github import fetch_recent_commits
from tools.jira import log_jira_time
from agents.prompt import SYSTEM_PROMPT, WorkLogExtraction
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage


# Configure our logger
logger = get_logger('AgentGraph')


# Define state structure
class GraphState(TypedDict):
    # Inputs provided by user/database
    target_ticket_id: str
    manual_text: str
    github_token: str
    repo_name: str
    jira_email: str
    jira_token: str
    jira_url: str
    
    # Data generated during execution
    commits: List[Dict[str, str]]
    worklogs: List[Any]  # Will hold Pydantic JiraWorklog objects
    results: List[Dict[str, Any]] # Final status of Jira API calls


# Define the nodes
def node_fetch_commits(state: GraphState):
    logger.info("===== Executing Node: Fetching GitHub Commits... =====")
    commits = fetch_recent_commits(state['github_token'], state['repo_name'])

    return {'commits': commits}


def node_extract_worklogs(state: GraphState):
    logger.info("===== Executing Node: Synthesizing data with Gemini 2.5 Flash... =====")

    # Initialize gemini
    llm = ChatGoogleGenerativeAI(model = 'gemini-2.5-flash', temperature = 0.1, max_output_tokens = 500)

    # Bind our pydantic schema to force a JSON output
    structured_llm = llm.with_structured_output(WorkLogExtraction)

    # Construct the payload
    user_payload = (
        f"Target Ticket ID: {state.get('target_ticket_id', 'UNKNOWN')}\n"
        f"Manual Notes:\n{state.get('manual_text', 'None')}\n\n"
        f"Commits:\n{state.get('commits', [])}"
    )

    try:
        response: Any = structured_llm.invoke([
            SystemMessage(content = SYSTEM_PROMPT),
            HumanMessage(content = user_payload)
        ])
        logger.info(f"Gemini successfully generated {len(response.worklogs)} worklogs.")

        return {"worklogs": response.worklogs}
    except Exception as e:
        logger.error(f"===== Gemini failed to extract worklogs: {e} =====")
        return {"worklogs": []}


def node_log_to_jira(state: GraphState):
    logger.info("===== Executing Node: Pushing data to Jira... =====")
    results = []

    for wl in state.get('worklogs', []):
        # Skip dummy tickets
        if wl.ticket_id.upper() in ["N/A", "NONE", "UNKNOWN"]:
            logger.warning(f"===== Skipping invalid ticket ID: {wl.ticket_id} =====")
            continue

        success = log_jira_time(
            jira_email = state["jira_email"],
            jira_token = state["jira_token"],
            jira_url = state["jira_url"],
            issue_id = wl.ticket_id,
            time_spent = wl.time_spent,
            comment = wl.comment
        )
        results.append({"ticket": wl.ticket_id, "time": wl.time_spent, "success": success})
        
    return {"results": results}


# Build and Compile the Graph
workflow = StateGraph(GraphState)

# Add our nodes
workflow.add_node("fetch_commits", node_fetch_commits)
workflow.add_node("extract_worklogs", node_extract_worklogs)
workflow.add_node("log_to_jira", node_log_to_jira)

# Define the sequence
workflow.add_edge(START, "fetch_commits")
workflow.add_edge("fetch_commits", "extract_worklogs")
workflow.add_edge("extract_worklogs", "log_to_jira")
workflow.add_edge("log_to_jira", END)

# Compile into an executable application
app = workflow.compile()

# Quick local testing block
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_state: GraphState = {
        "target_ticket_id": "TKT-ID", 
        "manual_text": "Finished the API integration and resolved the PR comments.",
        # 2. Add '' or ""' to guarantee these resolve to strings, not None
        "github_token": os.getenv("GITHUB_TOKEN") or "",
        "repo_name": "your-github-username/repo-name",
        "jira_email": os.getenv("JIRA_EMAIL") or "",
        "jira_token": os.getenv("JIRA_TOKEN") or "",
        "jira_url": "https://your-domain-name.atlassian.net",
        "commits": [],   
        "worklogs": [],  
        "results": []    
    }
    
    print("\n--- Starting LangGraph Execution ---")
    final_state = app.invoke(test_state)
    print("\n--- Execution Complete ---")
    print("Final Results:", final_state.get("results"))
