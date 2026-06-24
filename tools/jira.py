import os
from utils.logger import get_logger
from jira import JIRA


# Initialize out logger
logger = get_logger('JiraTool')


def log_jira_time(jira_email: str, jira_token: str, jira_url: str, issue_id: str, time_spent: str, comment: str) -> bool:
    try:
        logger.info(f"===== Attempting to log {time_spent} to ticket {issue_id}... =====")
        options = {'server': jira_url}
        jira = JIRA(options = options, basic_auth = (jira_email, jira_token))

        if not jira:
            logger.error("===== Failed to authenticate with Jira. Check your credentials. =====")
            return False
        
        jira.add_worklog(issue = issue_id, timeSpent = time_spent, comment = comment)
        logger.info(f"===== Successfully logged {time_spent} to ticket {issue_id} =====")

        return True
    except Exception as e:
        logger.error(f"===== Failed logging time to Jira issue {issue_id}: {str(e)} =====")
        return False


# Quick local testing block
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    TEST_EMAIL = os.getenv("JIRA_EMAIL")
    TEST_TOKEN = os.getenv("JIRA_TOKEN")
    TEST_URL = "https://your-domain-name.atlassian.net/"
    TEST_ISSUE = "YOUR_ISSUE_ID" # Replace with a real ticket id in your sandbox
    
    if TEST_EMAIL and TEST_TOKEN and TEST_ISSUE != "PROJ-123":
        logger.info("===== Testing Jira Tool... =====")
        success = log_jira_time(TEST_EMAIL, TEST_TOKEN, TEST_URL, TEST_ISSUE, "15m", "Automated test worklog via API.")
        logger.info(f"===== Result: {success} =====")
    else:
        logger.error("===== Skipping local test. Please populate JIRA variables in your environment. =====")
