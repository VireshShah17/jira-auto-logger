import os
from utils.logger import get_logger
from datetime import datetime, timedelta, timezone
from github import Github, Auth


# Initialize our logger
logger = get_logger("GitHubTool")


def fetch_recent_commits(github_token: str, repo_name: str) -> list:
    """
        Fetches commit messages authored by the authenticated user 
        in a specific repository within the last 24 hours.
    """

    try:
        auth = Auth.Token(github_token)
        g = Github(auth = auth)
        user = g.get_user()
        user_login = user.login

        logger.info(f"===== Authenticating user '{user_login}' for repo '{repo_name}' =====")
        repo = g.get_repo(repo_name)

        time_threshold = datetime.now(timezone.utc) - timedelta(days=1)
        commits = repo.get_commits(since = time_threshold)

        recent_commits = []
        for commit in commits:
            if commit.author and commit.author.login == user_login:
                recent_commits.append({
                    "sha": commit.sha[:7],
                    "message": commit.commit.message.strip(),
                    "date": commit.commit.author.date.isoformat()
                })
        
        logger.info(f"===== Successfully retrieved {len(recent_commits)} recent commits. =====")

        return recent_commits
    except Exception as e:
        logger.error(f"Failed to fetch github commits: {str(e)}")

        return []


# Quick local testing block
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Provide a test repo you have access to (e.g., "username/repo")
    TEST_REPO = "YourGitHubUserName/YourRepoName" 
    TEST_TOKEN = os.getenv("GITHUB_TOKEN") # Temporarily put a token in your .env for this test
    
    if TEST_TOKEN:
        print("Testing GitHub Tool...")
        logs = fetch_recent_commits(TEST_TOKEN, TEST_REPO)
        print(f"Found {len(logs)} commits in the last 24 hours:")
        for log in logs:
            print(f"- [{log['sha']}] {log['message']}")
    else:
        print("Skipping local test. Please populate GITHUB_TOKEN and TEST_REPO in your environment.")
