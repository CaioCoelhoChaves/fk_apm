#!/usr/bin/env python3
"""
Linear API CLI Helper for linear-workflow skill.
Zero-dependency Python script using standard library urllib to interact with Linear's GraphQL API.
"""

import os
import sys
import json
import re
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, List

LINEAR_GRAPHQL_ENDPOINT = "https://api.linear.app/graphql"

def resolve_api_key(explicit_key: Optional[str] = None) -> Optional[str]:
    """
    Dynamically resolve Linear API key in priority order:
    1. Explicit argument
    2. Environment variables: LINEAR_API_KEY, LINEAR_TOKEN
    3. Configuration file: .linear.json, .linearrc (searching current and parent dirs)
    4. .env file
    """
    if explicit_key:
        return explicit_key.strip()

    # 1. Environment variables
    env_key = os.environ.get("LINEAR_API_KEY") or os.environ.get("LINEAR_TOKEN")
    if env_key:
        return env_key.strip()

    cwd = Path.cwd().resolve()
    candidates = [cwd] + list(cwd.parents)

    # 2. Config files (.linear.json, .linearrc)
    for folder in candidates:
        for filename in [".linear.json", ".linearrc", "linear.json"]:
            config_file = folder / filename
            if config_file.is_file():
                try:
                    data = json.loads(config_file.read_text(encoding="utf-8"))
                    key = data.get("apiKey") or data.get("api_key") or data.get("token")
                    if key:
                        return key.strip()
                except Exception:
                    pass

    # 3. .env files
    for folder in candidates:
        env_file = folder / ".env"
        if env_file.is_file():
            try:
                content = env_file.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k in ("LINEAR_API_KEY", "LINEAR_TOKEN"):
                            return v
            except Exception:
                pass

    return None

def execute_graphql(api_key: str, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a GraphQL query/mutation against Linear API."""
    payload = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        LINEAR_GRAPHQL_ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": api_key if api_key.startswith("Bearer ") else api_key,
            "User-Agent": "fk_apm-linear-workflow/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            result = json.loads(response.read().decode("utf-8"))
            if "errors" in result:
                return {"success": False, "errors": result["errors"]}
            return {"success": True, "data": result.get("data", {})}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        return {"success": False, "error": f"HTTP {e.code}: {e.reason}", "details": err_body}
    except Exception as e:
        return {"success": False, "error": str(e)}

# GraphQL Queries & Mutations
VIEWER_QUERY = """
query ViewerQuery {
  viewer {
    id
    name
    email
  }
  teams {
    nodes {
      id
      name
      key
    }
  }
}
"""

LIST_PROJECTS_QUERY = """
query ListProjectsQuery($filter: ProjectFilter) {
  projects(filter: $filter, first: 50) {
    nodes {
      id
      name
      description
      state
      slugId
      url
      teams {
        nodes {
          id
          name
          key
        }
      }
    }
  }
}
"""

SEARCH_ISSUES_QUERY = """
query SearchIssuesQuery($filter: IssueFilter, $term: String) {
  issueSearch(query: $term, filter: $filter, first: 30) {
    nodes {
      id
      identifier
      title
      description
      url
      state {
        id
        name
        type
      }
      project {
        id
        name
      }
      labels {
        nodes {
          id
          name
        }
      }
    }
  }
}
"""

PROJECT_ISSUES_QUERY = """
query ProjectIssuesQuery($projectId: ID!) {
  project(id: $projectId) {
    id
    name
    issues(first: 50) {
      nodes {
        id
        identifier
        title
        description
        url
        state {
          id
          name
          type
        }
        labels {
          nodes {
            id
            name
          }
        }
      }
    }
  }
}
"""

LIST_STATES_QUERY = """
query ListStatesQuery($teamId: ID!) {
  team(id: $teamId) {
    id
    name
    states {
      nodes {
        id
        name
        type
        position
      }
    }
    labels {
      nodes {
        id
        name
        color
      }
    }
  }
}
"""

CREATE_ISSUE_MUTATION = """
mutation CreateIssue($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue {
      id
      identifier
      title
      url
      state {
        id
        name
      }
      project {
        id
        name
      }
      labels {
        nodes {
          id
          name
        }
      }
    }
  }
}
"""

UPDATE_ISSUE_MUTATION = """
mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
  issueUpdate(id: $id, input: $input) {
    success
    issue {
      id
      identifier
      title
      url
      state {
        id
        name
      }
    }
  }
}
"""

CREATE_COMMENT_MUTATION = """
mutation CreateComment($input: CommentCreateInput!) {
  commentCreate(input: $input) {
    success
    comment {
      id
      body
      createdAt
    }
  }
}
"""

CREATE_LABEL_MUTATION = """
mutation CreateLabel($input: IssueLabelCreateInput!) {
  issueLabelCreate(input: $input) {
    success
    issueLabel {
      id
      name
    }
  }
}
"""

def cmd_auth_check(api_key: str):
    res = execute_graphql(api_key, VIEWER_QUERY)
    print(json.dumps(res, indent=2, ensure_ascii=False))

def cmd_find_project(api_key: str, name_query: str):
    res = execute_graphql(api_key, LIST_PROJECTS_QUERY)
    if not res.get("success"):
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    projects = res["data"]["projects"]["nodes"]
    clean_query = re.sub(r"[\-_]", " ", name_query).strip().lower()
    
    # 1. Exact match
    matched = [p for p in projects if p["name"].lower() == clean_query]
    
    # 2. Substring or parent project match
    if not matched:
        # Check if project name is prefix or substring (e.g. query "Rent Easy Frontend" matches project "Rent Easy")
        matched = [p for p in projects if p["name"].lower() in clean_query or clean_query in p["name"].lower()]

    output = {
        "success": True,
        "query": name_query,
        "found": len(matched) > 0,
        "matches": matched,
        "all_projects": [{"id": p["id"], "name": p["name"]} for p in projects]
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))

def cmd_list_projects(api_key: str):
    res = execute_graphql(api_key, LIST_PROJECTS_QUERY)
    print(json.dumps(res, indent=2, ensure_ascii=False))

def cmd_get_project_issues(api_key: str, project_id: str):
    res = execute_graphql(api_key, PROJECT_ISSUES_QUERY, {"projectId": project_id})
    print(json.dumps(res, indent=2, ensure_ascii=False))

def cmd_search_issues(api_key: str, term: str, project_id: Optional[str] = None):
    # Search with term
    res = execute_graphql(api_key, SEARCH_ISSUES_QUERY, {"term": term})
    if not res.get("success"):
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    issues = res["data"].get("issueSearch", {}).get("nodes", [])
    if project_id:
        issues = [i for i in issues if i.get("project") and i["project"].get("id") == project_id]

    print(json.dumps({"success": True, "count": len(issues), "issues": issues}, indent=2, ensure_ascii=False))

def cmd_list_states(api_key: str, team_id: str):
    res = execute_graphql(api_key, LIST_STATES_QUERY, {"teamId": team_id})
    print(json.dumps(res, indent=2, ensure_ascii=False))

def resolve_state_id(api_key: str, team_id: str, state_name: str) -> Optional[str]:
    res = execute_graphql(api_key, LIST_STATES_QUERY, {"teamId": team_id})
    if not res.get("success"):
        return None
    states = res["data"]["team"]["states"]["nodes"]
    target = state_name.strip().lower()
    
    # Exact or fuzzy match
    for s in states:
        if s["name"].lower() == target:
            return s["id"]
            
    # Fuzzy alias mapping
    aliases = {
        "backlog": ["backlog"],
        "todo": ["todo", "to do", "a fazer"],
        "technical analysis": ["technical analysis", "analysis", "analise tecnica", "análise técnica", "spike", "investigation"],
        "in progress": ["in progress", "started", "doing", "em progresso", "em andamento"],
        "in review": ["in review", "review", "revisão", "em revisão", "pr"],
        "done": ["done", "completed", "concluído", "finalizado"],
        "canceled": ["canceled", "cancelled", "cancelado"],
        "duplicate": ["duplicate", "duplicado"]
    }
    for canonical, variations in aliases.items():
        if target in variations:
            for s in states:
                if s["name"].lower() in variations:
                    return s["id"]
    return None

def resolve_or_create_label_id(api_key: str, team_id: str, label_name: str) -> Optional[str]:
    res = execute_graphql(api_key, LIST_STATES_QUERY, {"teamId": team_id})
    if not res.get("success"):
        return None
    labels = res["data"]["team"]["labels"]["nodes"]
    target = label_name.strip().lower()
    for l in labels:
        if l["name"].lower() == target:
            return l["id"]

    # Try creating the label if missing
    create_res = execute_graphql(api_key, CREATE_LABEL_MUTATION, {
        "input": {"name": label_name.strip(), "teamId": team_id}
    })
    if create_res.get("success"):
        return create_res["data"]["issueLabelCreate"]["issueLabel"]["id"]
    return None

def cmd_create_issue(api_key: str, team_id: str, title: str, description: str, project_id: Optional[str] = None, state_name: Optional[str] = None, labels: Optional[List[str]] = None):
    input_data: Dict[str, Any] = {
        "teamId": team_id,
        "title": title,
        "description": description or ""
    }
    if project_id:
        input_data["projectId"] = project_id
    if state_name:
        state_id = resolve_state_id(api_key, team_id, state_name)
        if state_id:
            input_data["stateId"] = state_id
    if labels:
        label_ids = []
        for lbl in labels:
            lid = resolve_or_create_label_id(api_key, team_id, lbl)
            if lid:
                label_ids.append(lid)
        if label_ids:
            input_data["labelIds"] = label_ids

    res = execute_graphql(api_key, CREATE_ISSUE_MUTATION, {"input": input_data})
    print(json.dumps(res, indent=2, ensure_ascii=False))

def cmd_update_issue(api_key: str, issue_id: str, team_id: Optional[str] = None, state_name: Optional[str] = None, comment: Optional[str] = None):
    input_data: Dict[str, Any] = {}
    if state_name and team_id:
        state_id = resolve_state_id(api_key, team_id, state_name)
        if state_id:
            input_data["stateId"] = state_id

    res = execute_graphql(api_key, UPDATE_ISSUE_MUTATION, {"id": issue_id, "input": input_data})
    
    if comment:
        execute_graphql(api_key, CREATE_COMMENT_MUTATION, {
            "input": {"issueId": issue_id, "body": comment}
        })

    print(json.dumps(res, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(description="Linear GraphQL API helper CLI")
    parser.add_argument("--api-key", help="Linear Personal API Key (optional, defaults to dynamic discovery)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # auth-check
    subparsers.add_parser("auth-check", help="Verify credentials and list current viewer & teams")

    # list-projects
    subparsers.add_parser("list-projects", help="List all projects in workspace")

    # find-project
    find_p = subparsers.add_parser("find-project", help="Search project by name or subproject pattern")
    find_p.add_argument("name", help="Project name query")

    # project-issues
    p_issues = subparsers.add_parser("project-issues", help="List issues in project")
    p_issues.add_argument("project_id", help="Linear Project ID")

    # search-issues
    s_issues = subparsers.add_parser("search-issues", help="Search issues by query text")
    s_issues.add_argument("term", help="Search term")
    s_issues.add_argument("--project-id", help="Filter by Linear Project ID")

    # list-states
    l_states = subparsers.add_parser("list-states", help="List team states and labels")
    l_states.add_argument("team_id", help="Linear Team ID")

    # create-issue
    c_issue = subparsers.add_parser("create-issue", help="Create issue in Linear")
    c_issue.add_argument("--team-id", required=True, help="Linear Team ID")
    c_issue.add_argument("--title", required=True, help="Issue title")
    c_issue.add_argument("--description", default="", help="Issue description")
    c_issue.add_argument("--project-id", help="Linear Project ID")
    c_issue.add_argument("--state", help="State name (e.g., 'Backlog', 'Todo', 'In Progress')")
    c_issue.add_argument("--label", action="append", dest="labels", help="Labels to attach (e.g. Front, Back)")

    # update-issue
    u_issue = subparsers.add_parser("update-issue", help="Update issue state or add comment")
    u_issue.add_argument("issue_id", help="Linear Issue ID or identifier")
    u_issue.add_argument("--team-id", help="Linear Team ID (required if changing state)")
    u_issue.add_argument("--state", help="New state name (e.g., 'Technical Analysis', 'In Progress', 'In Review', 'Done')")
    u_issue.add_argument("--comment", help="Comment body to post")

    args = parser.parse_args()

    api_key = resolve_api_key(args.api_key)
    if not api_key:
        print(json.dumps({
            "success": False,
            "error": "No Linear API key found.",
            "hint": "Set LINEAR_API_KEY environment variable or create a .linear.json file with {'apiKey': '...'}"
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    if args.command == "auth-check":
        cmd_auth_check(api_key)
    elif args.command == "list-projects":
        cmd_list_projects(api_key)
    elif args.command == "find-project":
        cmd_find_project(api_key, args.name)
    elif args.command == "project-issues":
        cmd_get_project_issues(api_key, args.project_id)
    elif args.command == "search-issues":
        cmd_search_issues(api_key, args.term, args.project_id)
    elif args.command == "list-states":
        cmd_list_states(api_key, args.team_id)
    elif args.command == "create-issue":
        cmd_create_issue(api_key, args.team_id, args.title, args.description, args.project_id, args.state, args.labels)
    elif args.command == "update-issue":
        cmd_update_issue(api_key, args.issue_id, args.team_id, args.state, args.comment)

if __name__ == "__main__":
    main()
