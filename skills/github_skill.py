"""
skills/github_skill.py — Phase 7: GitHub Skill
Interfaces with the GitHub REST API to check repos, issues, PRs, and notifications.
Requires a GitHub Personal Access Token (PAT) set in Settings.
"""
import re
from typing import List
from skills.base_skill import BaseSkill


class GitHubSkill(BaseSkill):
    """Connects to GitHub API for repo management and notifications."""

    @property
    def name(self) -> str:
        return "github"

    @property
    def description(self) -> str:
        return "GitHub integration: list repos, check PRs, view issues, get notifications. Requires GitHub PAT in Settings."

    @property
    def triggers(self) -> List[str]:
        return [
            "github", "my repos", "my repositories", "pull requests", "open prs",
            "github issues", "github notifications", "check github", "list my repos",
            "open issues", "github status", "create issue", "commit history"
        ]

    def execute(self, user_input: str, core=None) -> str:
        text_lower = user_input.lower()

        # Get token from config if available
        token = ""
        if core and hasattr(core, "config"):
            token = core.config.get("github_token", "")

        if not token:
            return ("GitHub skill needs a Personal Access Token (PAT).\n"
                    "Go to **Settings** → add your GitHub PAT.\n"
                    "Create one at: https://github.com/settings/tokens")

        if any(w in text_lower for w in ["notification", "unread"]):
            return self._get_notifications(token)
        elif any(w in text_lower for w in ["repos", "repositories", "list my repos"]):
            return self._list_repos(token)
        elif any(w in text_lower for w in ["pull request", "pr", "prs"]):
            repo = self._extract_repo(user_input)
            return self._list_prs(token, repo)
        elif any(w in text_lower for w in ["issue", "issues"]):
            repo = self._extract_repo(user_input)
            if "create" in text_lower:
                title = re.sub(r'.*create\s+(?:an?\s+)?issue\s+', '', user_input, flags=re.IGNORECASE).strip()
                return self._create_issue(token, repo, title) if repo else "Please specify a repo (e.g. 'create issue fix login bug in myrepo')"
            return self._list_issues(token, repo)
        elif any(w in text_lower for w in ["commit", "history"]):
            repo = self._extract_repo(user_input)
            return self._get_commits(token, repo)
        else:
            return self._get_profile(token)

    def _api(self, token: str, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Makes a GitHub API request."""
        import requests
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        url = f"https://api.github.com{endpoint}"
        try:
            if method == "POST":
                resp = requests.post(url, headers=headers, json=data, timeout=8)
            else:
                resp = requests.get(url, headers=headers, timeout=8)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def _get_profile(self, token: str) -> str:
        data = self._api(token, "/user")
        if "error" in data:
            return f"GitHub API error: {data['error']}"
        name = data.get("name") or data.get("login", "Unknown")
        repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        return (f"### 🐙 GitHub Profile\n"
                f"**User**: {name} (@{data.get('login', '')})\n"
                f"**Public Repos**: {repos} | **Followers**: {followers}\n"
                f"**Profile**: {data.get('html_url', '')}")

    def _list_repos(self, token: str) -> str:
        data = self._api(token, "/user/repos?sort=updated&per_page=10")
        if isinstance(data, dict) and "error" in data:
            return f"GitHub API error: {data['error']}"
        if not isinstance(data, list):
            return "Could not fetch repositories."
        lines = ["### 📁 Your Most Recently Updated Repos"]
        for repo in data[:10]:
            lang = repo.get("language") or "—"
            stars = repo.get("stargazers_count", 0)
            lines.append(f"• **{repo['name']}** ({lang}) ⭐{stars} — {repo.get('html_url', '')}")
        return "\n".join(lines)

    def _list_prs(self, token: str, repo: str = None) -> str:
        if not repo:
            return "Please specify a repository name. Example: 'show PRs in myproject'"
        user_data = self._api(token, "/user")
        owner = user_data.get("login", "")
        data = self._api(token, f"/repos/{owner}/{repo}/pulls?state=open")
        if isinstance(data, dict) and "message" in data:
            return f"Could not find repo '{repo}': {data['message']}"
        if not isinstance(data, list) or not data:
            return f"No open pull requests found in {repo}."
        lines = [f"### 🔀 Open PRs in {repo}"]
        for pr in data[:10]:
            lines.append(f"• **#{pr['number']}** {pr['title']} — by @{pr['user']['login']}")
        return "\n".join(lines)

    def _list_issues(self, token: str, repo: str = None) -> str:
        if not repo:
            # Show all user's issues
            data = self._api(token, "/issues?filter=assigned&state=open&per_page=10")
        else:
            user_data = self._api(token, "/user")
            owner = user_data.get("login", "")
            data = self._api(token, f"/repos/{owner}/{repo}/issues?state=open&per_page=10")
        if isinstance(data, dict) and "error" in data:
            return f"GitHub error: {data['error']}"
        if not isinstance(data, list) or not data:
            return "No open issues found."
        lines = [f"### 🐛 Open Issues{' in ' + repo if repo else ' (assigned to you)'}"]
        for issue in data[:10]:
            lines.append(f"• **#{issue['number']}** {issue['title']}")
        return "\n".join(lines)

    def _create_issue(self, token: str, repo: str, title: str) -> str:
        user_data = self._api(token, "/user")
        owner = user_data.get("login", "")
        data = self._api(token, f"/repos/{owner}/{repo}/issues", method="POST",
                         data={"title": title, "body": "Created by Jarvis AI Assistant"})
        if "html_url" in data:
            return f"✅ Issue created: **{title}**\n{data['html_url']}"
        return f"Failed to create issue: {data.get('message', 'Unknown error')}"

    def _get_commits(self, token: str, repo: str = None) -> str:
        if not repo:
            return "Please specify a repo name. Example: 'show commits in myproject'"
        user_data = self._api(token, "/user")
        owner = user_data.get("login", "")
        data = self._api(token, f"/repos/{owner}/{repo}/commits?per_page=5")
        if isinstance(data, dict) and "message" in data:
            return f"Could not fetch commits: {data['message']}"
        if not isinstance(data, list) or not data:
            return f"No commits found in {repo}."
        lines = [f"### 📜 Recent Commits in {repo}"]
        for commit in data:
            sha = commit["sha"][:7]
            msg = commit["commit"]["message"].split("\n")[0][:80]
            author = commit["commit"]["author"]["name"]
            date = commit["commit"]["author"]["date"][:10]
            lines.append(f"• `{sha}` [{date}] {msg} — *{author}*")
        return "\n".join(lines)

    def _get_notifications(self, token: str) -> str:
        data = self._api(token, "/notifications?all=false&per_page=10")
        if isinstance(data, dict) and "error" in data:
            return f"GitHub error: {data['error']}"
        if not isinstance(data, list) or not data:
            return "✅ No unread GitHub notifications."
        lines = ["### 🔔 GitHub Notifications"]
        for n in data[:10]:
            repo = n.get("repository", {}).get("full_name", "")
            subject = n.get("subject", {}).get("title", "")
            ntype = n.get("subject", {}).get("type", "")
            lines.append(f"• [{ntype}] **{repo}**: {subject}")
        return "\n".join(lines)

    def _extract_repo(self, text: str) -> str:
        """Extracts a repo name from phrases like 'issues in myproject'."""
        patterns = [
            r'(?:in|for|of|repo)\s+([A-Za-z0-9_\-\.]+)',
            r'([A-Za-z0-9_\-\.]+)\s+(?:repo|repository)',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return ""
