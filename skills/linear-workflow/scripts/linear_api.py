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
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

# Ensure stdout and stderr use UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

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

GET_ISSUE_QUERY = """
query GetIssueQuery($id: String!) {
  issue(id: $id) {
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
    team {
      id
      name
      key
    }
    labels {
      nodes {
        id
        name
      }
    }
    comments(last: 15) {
      nodes {
        id
        body
        createdAt
      }
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
query SearchIssuesQuery($filter: IssueFilter) {
  issues(filter: $filter, first: 30) {
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
      team {
        id
        name
        key
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
query ProjectIssuesQuery($projectId: String!) {
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
query ListStatesQuery($teamId: String!) {
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

def check_comment_idempotency(comments: List[Dict[str, Any]], target_body: str, window_minutes: float = 10.0) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if an identical comment was already posted within the specified time window.
    Returns (is_duplicate, duplicate_comment_node).
    """
    clean_target = target_body.strip()
    now = datetime.now(timezone.utc)

    for c in comments:
        clean_existing = (c.get("body") or "").strip()
        if clean_existing == clean_target:
            created_at_str = c.get("createdAt")
            if created_at_str:
                try:
                    dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    diff_minutes = (now - dt).total_seconds() / 60.0
                    if diff_minutes <= window_minutes:
                        return True, c
                except Exception:
                    # If date parsing fails, compare text identically
                    return True, c
    return False, None

def cmd_auth_check(api_key: str):
    res = execute_graphql(api_key, VIEWER_QUERY)
    print(json.dumps(res, indent=2, ensure_ascii=False))

def cmd_get_issue(api_key: str, issue_id: str):
    res = execute_graphql(api_key, GET_ISSUE_QUERY, {"id": issue_id})
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
    # If term looks like an issue key (e.g. FAL-24), try direct lookup first
    if re.match(r"^[A-Za-z]+-\d+$", term.strip()):
        direct = execute_graphql(api_key, GET_ISSUE_QUERY, {"id": term.strip()})
        if direct.get("success") and direct.get("data", {}).get("issue"):
            issue_node = direct["data"]["issue"]
            if not project_id or (issue_node.get("project") and issue_node["project"].get("id") == project_id):
                print(json.dumps({"success": True, "count": 1, "issues": [issue_node]}, indent=2, ensure_ascii=False))
                return

    # GraphQL filter using modern issues(filter: ...)
    filter_conditions: List[Dict[str, Any]] = [
        {
            "or": [
                {"title": {"containsIgnoreCase": term}},
                {"description": {"containsIgnoreCase": term}}
            ]
        }
    ]
    if project_id:
        filter_conditions.append({"project": {"id": {"eq": project_id}}})

    filter_dict = {"and": filter_conditions} if len(filter_conditions) > 1 else filter_conditions[0]
    res = execute_graphql(api_key, SEARCH_ISSUES_QUERY, {"filter": filter_dict})
    if not res.get("success"):
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    issues = res["data"].get("issues", {}).get("nodes", [])
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
    
    # Exact match
    for s in states:
        if s["name"].lower() == target:
            return s["id"]
            
    # Fuzzy alias mapping
    aliases = {
        "backlog": ["backlog"],
        "technical analysis": ["technical analysis", "analysis", "analise tecnica", "análise técnica", "spike", "investigation"],
        "todo": ["todo", "to do", "a fazer"],
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

def cmd_create_issue(
    api_key: str,
    team_id: str,
    title: str,
    description: str = "",
    project_id: Optional[str] = None,
    state_name: Optional[str] = None,
    labels: Optional[List[str]] = None,
    description_file: Optional[str] = None
):
    resolved_description = description
    if description_file:
        try:
            resolved_description = Path(description_file).read_text(encoding="utf-8")
        except Exception as e:
            print(json.dumps({
                "success": False,
                "error": f"Failed to read description file '{description_file}': {e}"
            }, indent=2, ensure_ascii=False))
            return

    input_data: Dict[str, Any] = {
        "teamId": team_id,
        "title": title,
        "description": resolved_description or ""
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

def cmd_update_issue(
    api_key: str,
    issue_id: str,
    team_id: Optional[str] = None,
    state_name: Optional[str] = None,
    comment: Optional[str] = None,
    force_comment: bool = False,
    description: Optional[str] = None,
    description_file: Optional[str] = None,
    title: Optional[str] = None,
    comment_file: Optional[str] = None
):
    """
    Atomic update for Linear issue:
    1. Resolves issue UUID, team, and recent comments.
    2. Updates state, title, and/or description (if requested).
    3. Posts comment with idempotency protection (skips duplicates posted within 10 min).
    """
    # 1. Fetch current issue context
    issue_res = execute_graphql(api_key, GET_ISSUE_QUERY, {"id": issue_id})
    if not issue_res.get("success") or not issue_res.get("data", {}).get("issue"):
        print(json.dumps({
            "success": False,
            "error": f"Issue '{issue_id}' not found.",
            "details": issue_res
        }, indent=2, ensure_ascii=False))
        return

    issue_data = issue_res["data"]["issue"]
    real_uuid = issue_data["id"]
    resolved_team_id = team_id or (issue_data.get("team") and issue_data["team"].get("id"))

    output: Dict[str, Any] = {
        "success": True,
        "issue": {
            "id": real_uuid,
            "identifier": issue_data.get("identifier"),
            "title": issue_data.get("title")
        }
    }

    # Handle description resolution
    resolved_description = description
    if description_file:
        try:
            resolved_description = Path(description_file).read_text(encoding="utf-8")
        except Exception as e:
            output["description_update"] = {
                "success": False,
                "error": f"Failed to read description file '{description_file}': {e}"
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
            return

    # Handle comment resolution
    resolved_comment = comment
    if comment_file:
        try:
            resolved_comment = Path(comment_file).read_text(encoding="utf-8")
        except Exception as e:
            output["comment"] = {
                "success": False,
                "error": f"Failed to read comment file '{comment_file}': {e}"
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
            return

    # 2. Update state and/or description if requested
    update_input: Dict[str, Any] = {}
    if state_name:
        if not resolved_team_id:
            output["state_update"] = {
                "success": False,
                "error": "Cannot resolve team ID to update state. Provide --team-id explicitly."
            }
        else:
            state_id = resolve_state_id(api_key, resolved_team_id, state_name)
            if not state_id:
                output["state_update"] = {
                    "success": False,
                    "error": f"State '{state_name}' not found for team '{resolved_team_id}'."
                }
            else:
                update_input["stateId"] = state_id

    if title is not None and title.strip():
        update_input["title"] = title.strip()

    if resolved_description is not None:
        update_input["description"] = resolved_description

    if update_input:
        update_res = execute_graphql(api_key, UPDATE_ISSUE_MUTATION, {
            "id": real_uuid,
            "input": update_input
        })
        if update_res.get("success"):
            if "stateId" in update_input:
                output["state_update"] = {
                    "success": True,
                    "state": state_name,
                    "stateId": update_input["stateId"]
                }
            if "title" in update_input:
                output["title_update"] = {
                    "success": True,
                    "updated": True,
                    "title": update_input["title"]
                }
                output["issue"]["title"] = update_input["title"]
            if "description" in update_input:
                output["description_update"] = {
                    "success": True,
                    "updated": True,
                    "length": len(resolved_description)
                }
        else:
            if "stateId" in update_input:
                output["state_update"] = update_res
            if "title" in update_input:
                output["title_update"] = update_res
            if "description" in update_input:
                output["description_update"] = update_res

    # 3. Add comment if requested with idempotency check
    if resolved_comment:
        existing_comments = issue_data.get("comments", {}).get("nodes", [])
        is_dup, dup_node = check_comment_idempotency(existing_comments, resolved_comment, window_minutes=10.0)

        if is_dup and not force_comment:
            output["comment"] = {
                "success": True,
                "created": False,
                "skipped": True,
                "reason": "Idempotent comment skipped: identical comment was posted within the last 10 minutes.",
                "existing_comment_id": dup_node.get("id") if dup_node else None
            }
        else:
            c_res = execute_graphql(api_key, CREATE_COMMENT_MUTATION, {
                "input": {"issueId": real_uuid, "body": resolved_comment}
            })
            if c_res.get("success"):
                output["comment"] = {
                    "success": True,
                    "created": True,
                    "comment_id": c_res["data"]["commentCreate"]["comment"]["id"]
                }
            else:
                output["comment"] = c_res

    print(json.dumps(output, indent=2, ensure_ascii=False))

def cmd_create_comment(
    api_key: str,
    issue_id: str,
    comment: Optional[str] = None,
    force: bool = False,
    comment_file: Optional[str] = None
):
    """Create comment on issue with idempotency protection."""
    if not comment and not comment_file:
        print(json.dumps({
            "success": False,
            "error": "Either a comment argument or --comment-file must be provided."
        }, indent=2, ensure_ascii=False))
        return
    cmd_update_issue(api_key, issue_id=issue_id, comment=comment, comment_file=comment_file, force_comment=force)

def main():
    parser = argparse.ArgumentParser(description="Linear GraphQL API helper CLI")
    parser.add_argument("--api-key", help="Linear Personal API Key (optional, defaults to dynamic discovery)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # auth-check
    subparsers.add_parser("auth-check", help="Verify credentials and list current viewer & teams")

    # get-issue
    get_i = subparsers.add_parser("get-issue", help="Get issue details, state, team and recent comments")
    get_i.add_argument("issue_id", help="Linear Issue ID or identifier (e.g. FAL-24)")

    # list-projects
    subparsers.add_parser("list-projects", help="List all projects in workspace")

    # find-project
    find_p = subparsers.add_parser("find-project", help="Search project by name or subproject pattern")
    find_p.add_argument("name", help="Project name query")

    # project-issues
    p_issues = subparsers.add_parser("project-issues", help="List issues in project")
    p_issues.add_argument("project_id", help="Linear Project ID")

    # search-issues
    s_issues = subparsers.add_parser("search-issues", help="Search issues by query text or identifier")
    s_issues.add_argument("term", help="Search term or issue key")
    s_issues.add_argument("--project-id", help="Filter by Linear Project ID")

    # list-states
    l_states = subparsers.add_parser("list-states", help="List team states and labels")
    l_states.add_argument("team_id", help="Linear Team ID")

    # create-issue
    c_issue = subparsers.add_parser("create-issue", help="Create issue in Linear")
    c_issue.add_argument("--team-id", required=True, help="Linear Team ID")
    c_issue.add_argument("--title", required=True, help="Issue title")
    c_issue.add_argument("--description", default="", help="Issue description")
    c_issue.add_argument("--description-file", help="Path to UTF-8 file containing issue description markdown")
    c_issue.add_argument("--project-id", help="Linear Project ID")
    c_issue.add_argument("--state", help="State name (e.g., 'Backlog', 'Todo', 'In Progress')")
    c_issue.add_argument("--label", action="append", dest="labels", help="Labels to attach (e.g. Front, Back)")

    # update-issue
    u_issue = subparsers.add_parser("update-issue", help="Update issue state, title, description, and/or add comment with idempotency protection")
    u_issue.add_argument("issue_id", help="Linear Issue ID or identifier")
    u_issue.add_argument("--team-id", help="Linear Team ID (optional, automatically resolved from issue if omitted)")
    u_issue.add_argument("--state", help="New state name (e.g., 'Technical Analysis', 'Todo', 'In Progress', 'In Review', 'Done')")
    u_issue.add_argument("--title", help="New issue title")
    u_issue.add_argument("--description", help="New issue description markdown")
    u_issue.add_argument("--description-file", help="Path to UTF-8 file containing new description markdown")
    u_issue.add_argument("--comment", help="Comment body to post")
    u_issue.add_argument("--comment-file", help="Path to UTF-8 file containing comment markdown body to post")
    u_issue.add_argument("--force-comment", action="store_true", help="Force posting comment even if identical comment exists within 10 minutes")

    # create-comment
    c_comment = subparsers.add_parser("create-comment", help="Create comment on issue with idempotency protection")
    c_comment.add_argument("issue_id", help="Linear Issue ID or identifier")
    c_comment.add_argument("comment", nargs="?", default=None, help="Comment body text")
    c_comment.add_argument("--comment-file", help="Path to UTF-8 file containing comment markdown body to post")
    c_comment.add_argument("--force", action="store_true", help="Force posting comment even if identical comment exists within 10 minutes")

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
    elif args.command == "get-issue":
        cmd_get_issue(api_key, args.issue_id)
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
        cmd_create_issue(
            api_key,
            args.team_id,
            args.title,
            args.description,
            args.project_id,
            args.state,
            args.labels,
            description_file=args.description_file
        )
    elif args.command == "update-issue":
        cmd_update_issue(
            api_key,
            args.issue_id,
            team_id=args.team_id,
            state_name=args.state,
            comment=args.comment,
            force_comment=args.force_comment,
            description=args.description,
            description_file=args.description_file,
            title=args.title,
            comment_file=args.comment_file
        )
    elif args.command == "create-comment":
        cmd_create_comment(api_key, args.issue_id, args.comment, args.force, comment_file=args.comment_file)

if __name__ == "__main__":
    main()
