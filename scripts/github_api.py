"""
Minimal GitHub GraphQL client.

Uses only the ambient GITHUB_TOKEN provided to every Actions run
(no personal access token, no third-party stats API). Every value
displayed in stats.svg / langs.svg / year.svg traces back to a call
in this file.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import requests

API_URL = "https://api.github.com/graphql"


class GitHubAPIError(RuntimeError):
    pass


def _token() -> str:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise GitHubAPIError(
            "GITHUB_TOKEN is not set. In Actions this is provided automatically; "
            "locally, export a token with 'read:user' and 'repo' (public_repo) scope."
        )
    return token


def _post(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
    }
    for attempt in range(3):
        resp = requests.post(
            API_URL,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=30,
        )
        if resp.status_code == 200:
            payload = resp.json()
            if "errors" in payload:
                raise GitHubAPIError(str(payload["errors"]))
            return payload["data"]
        if resp.status_code in (502, 503) and attempt < 2:
            time.sleep(2 * (attempt + 1))
            continue
        raise GitHubAPIError(f"GraphQL request failed: {resp.status_code} {resp.text[:300]}")
    raise GitHubAPIError("GraphQL request failed after retries")


_USER_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    name
    login
    createdAt
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
    repositories(
      first: 100
      ownerAffiliations: OWNER
      isFork: false
      privacy: PUBLIC
      orderBy: { field: STARGAZERS, direction: DESC }
    ) {
      totalCount
      nodes {
        name
        description
        stargazerCount
        forkCount
        primaryLanguage { name color }
        languages(first: 10, orderBy: { field: SIZE, direction: DESC }) {
          edges {
            size
            node { name color }
          }
        }
        isArchived
        pushedAt
      }
    }
    followers { totalCount }
  }
}
"""


@dataclass
class RepoStat:
    name: str
    description: str | None
    stars: int
    forks: int
    primary_language: str | None
    is_archived: bool
    languages: dict[str, int] = field(default_factory=dict)


@dataclass
class UserStats:
    login: str
    name: str
    joined_year: int
    total_contributions: int
    commits: int
    pull_requests: int
    reviews: int
    issues: int
    followers: int
    repos: list[RepoStat]
    calendar_days: list[tuple[str, int]]  # (ISO date, count)


def fetch_user_stats(login: str, year: int | None = None) -> UserStats:
    """Fetch one year of contribution + repo data for `login`.

    `year` defaults to the current calendar year, matching the
    "Timeline" / year.svg section of the profile.
    """
    target_year = year or datetime.now(timezone.utc).year
    date_from = f"{target_year}-01-01T00:00:00Z"
    date_to = f"{target_year}-12-31T23:59:59Z"

    data = _post(_USER_QUERY, {"login": login, "from": date_from, "to": date_to})
    user = data["user"]
    if user is None:
        raise GitHubAPIError(f"No such user: {login}")

    cc = user["contributionsCollection"]
    calendar = cc["contributionCalendar"]
    days: list[tuple[str, int]] = []
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days.append((day["date"], day["contributionCount"]))

    repos: list[RepoStat] = []
    for node in user["repositories"]["nodes"]:
        langs: dict[str, int] = {}
        for edge in node["languages"]["edges"]:
            langs[edge["node"]["name"]] = langs.get(edge["node"]["name"], 0) + edge["size"]
        repos.append(
            RepoStat(
                name=node["name"],
                description=node["description"],
                stars=node["stargazerCount"],
                forks=node["forkCount"],
                primary_language=(node["primaryLanguage"] or {}).get("name"),
                is_archived=node["isArchived"],
                languages=langs,
            )
        )

    return UserStats(
        login=user["login"],
        name=user["name"] or user["login"],
        joined_year=int(user["createdAt"][:4]),
        total_contributions=calendar["totalContributions"],
        commits=cc["totalCommitContributions"],
        pull_requests=cc["totalPullRequestContributions"],
        reviews=cc["totalPullRequestReviewContributions"],
        issues=cc["totalIssueContributions"],
        followers=user["followers"]["totalCount"],
        repos=repos,
        calendar_days=days,
    )


if __name__ == "__main__":
    login = sys.argv[1] if len(sys.argv) > 1 else "zaidbinnaveed"
    stats = fetch_user_stats(login)
    print(f"{stats.name} (@{stats.login}) — {stats.total_contributions} contributions in current year")
    print(f"{len(stats.repos)} public repos, {stats.followers} followers")
