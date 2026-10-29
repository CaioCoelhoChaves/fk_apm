#!/usr/bin/env python3
"""
Linear API CLI Helper for linear-workflow skill.
Zero-dependency Python script using standard library urllib to interact with Linear's GraphQL API.
"""

import os
import sys
import json
import re
import shutil
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

def _is_table_separator_cells(cells: List[str]) -> bool:
    """Return True if cells represent a Markdown table delimiter row (e.g. | :--- | --- |)."""
    if not cells:
        return False
    return all(bool(re.match(r"^:?-{1,}:?$", c.strip())) for c in cells if c.strip()) and any(c.strip() for c in cells)


def _split_table_row(line: str) -> List[str]:
    """Split a Markdown table line into stripped cells by unescaped pipe."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|") and not stripped.endswith(r"\|"):
        stripped = stripped[:-1]
    parts = re.split(r"(?<!\\)\|", stripped)
    return [p.strip() for p in parts]


def _normalize_separator_cell(cell: str) -> str:
    c = cell.strip()
    if not re.match(r"^:?-{1,}:?$", c):
        return "---"
    left = ":" if c.startswith(":") else ""
    right = ":" if c.endswith(":") else ""
    return f"{left}---{right}"


def _normalize_table_block(table_lines: List[str]) -> List[str]:
    """Normalize pipe alignment and column counts across a Markdown table block."""
    rows_cells = [_split_table_row(line) for line in table_lines]
    max_cols = max((len(r) for r in rows_cells), default=0)
    if max_cols == 0:
        return table_lines

    normalized: List[str] = []
    for cells in rows_cells:
        if _is_table_separator_cells(cells):
            norm_cells = [_normalize_separator_cell(c) for c in cells]
            while len(norm_cells) < max_cols:
                norm_cells.append("---")
        else:
            norm_cells = list(cells)
            while len(norm_cells) < max_cols:
                norm_cells.append("")
        normalized.append("| " + " | ".join(norm_cells[:max_cols]) + " |")
    return normalized


def sanitize_markdown_payload(text: Optional[str]) -> str:
    """
    Deterministic Markdown sanitizer for Linear and GitHub payloads:
    1. Normalizes CRLF/CR line breaks to LF (\\n).
    2. Strips invalid ASCII control characters (preserving \\n and \\t).
    3. Normalizes misaligned Markdown tables outside code fences.
    4. Automatically closes unclosed fenced code blocks (``` or ~~~).
    """
    if text is None:
        return ""
    if not text:
        return ""

    # 1. Normalize line endings
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Remove problematic control chars (keep \n = \x0a and \t = \x09)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)

    raw_lines = cleaned.split("\n")
    out_lines: List[str] = []
    table_buffer: List[str] = []
    active_fence: Optional[str] = None

    def flush_table_buffer():
        nonlocal table_buffer
        if not table_buffer:
            return
        has_separator = any(_is_table_separator_cells(_split_table_row(l)) for l in table_buffer)
        all_start_with_pipe = len(table_buffer) >= 2 and all(l.lstrip().startswith("|") for l in table_buffer)
        if len(table_buffer) >= 2 and (has_separator or all_start_with_pipe):
            out_lines.extend(_normalize_table_block(table_buffer))
        else:
            out_lines.extend(table_buffer)
        table_buffer = []

    for line in raw_lines:
        fence_match = re.match(r"^(\s*)(`{3,}|~{3,})(.*)$", line)
        if active_fence is None:
            if fence_match:
                flush_table_buffer()
                active_fence = fence_match.group(2)
                out_lines.append(line)
                continue

            # Candidate table line outside code block
            if "|" in line and not line.lstrip().startswith((">", "#", "- ", "* ")):
                table_buffer.append(line)
            else:
                flush_table_buffer()
                out_lines.append(line)
        else:
            # Inside code fence: check if this line closes the active fence
            fence_char = active_fence[0]
            fence_len = len(active_fence)
            close_pattern = rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$"
            if re.match(close_pattern, line):
                active_fence = None
            out_lines.append(line)

    flush_table_buffer()

    # 4. Close unclosed code fence at end of payload
    if active_fence is not None:
        out_lines.append(active_fence)

    return "\n".join(out_lines)


REQUIRED_PLAN_SECTIONS: List[Tuple[str, str]] = [
    ("Diagnóstico e Contexto", r"(?i)^#{1,4}\s*(?:\d+[\.\)]\s*)?diagn[oó]stico\b"),
    ("Arquitetura da Solução", r"(?i)^#{1,4}\s*(?:\d+[\.\)]\s*)?arquitetura\b"),
    ("Checklist de Arquivos Impactados", r"(?i)^#{1,4}\s*(?:\d+[\.\)]\s*)?(?:checklist\s+de\s+)?arquivos\s+impactados\b"),
    ("Estratégia de Testes", r"(?i)^#{1,4}\s*(?:\d+[\.\)]\s*)?(?:estrat[eé]gia\s+de\s+)?testes\b"),
    ("Plano Gitflow", r"(?i)^#{1,4}\s*(?:\d+[\.\)]\s*)?(?:plano\s+)?gitflow\b"),
]


def _extract_file_path_from_bullet(bullet_text: str) -> Optional[str]:
    """Extract a relative file path from a markdown checklist bullet line."""
    # Prefer backticked path first: - `path/to/file.py` (modificar)
    bt_match = re.search(r"`([^`]+)`", bullet_text)
    candidate = bt_match.group(1).strip() if bt_match else bullet_text.strip()
    if not bt_match:
        # Remove optional checkbox and trailing description after ':' or '('
        candidate = re.sub(r"^\[[ xX]\]\s*", "", candidate)
        candidate = re.split(r"\s+(?:\(|—|-|:)", candidate, maxsplit=1)[0].strip()
        candidate = candidate.rstrip(":")
    return candidate or None


def _resolve_spec_dir(
    target: str,
    resolved_repo: Path,
    specs_root: Optional[Path] = None
) -> Path:
    """Resolve feature specification directory across official Spec Kit (specs/ & .specify/feature.json) and legacy .specs/."""
    target_clean = (target or "").strip()

    if specs_root is not None:
        resolved_specs = specs_root.resolve()
        if not target_clean:
            return resolved_specs
        direct = resolved_specs / target_clean
        if direct.is_dir():
            return direct.resolve()
        # Try matching substring/prefix in specs_root
        if resolved_specs.is_dir():
            lower_target = target_clean.lower()
            for child in sorted(resolved_specs.iterdir()):
                if child.is_dir() and lower_target in child.name.lower():
                    return child.resolve()
        return direct.resolve()

    if target_clean:
        candidate_dir = Path(target_clean)
        if candidate_dir.is_dir():
            return candidate_dir.resolve()
        repo_rel = resolved_repo / target_clean
        if repo_rel.is_dir() and ("/" in target_clean or "\\" in target_clean):
            return repo_rel.resolve()

    # Check .specify/feature.json
    feature_json = resolved_repo / ".specify" / "feature.json"
    active_feature_dir: Optional[Path] = None
    if feature_json.is_file():
        try:
            fdata = json.loads(feature_json.read_text(encoding="utf-8"))
            fdir_val = fdata.get("feature_directory") if isinstance(fdata, dict) else None
            if isinstance(fdir_val, str) and fdir_val.strip():
                fdir_path = Path(fdir_val.strip())
                if not fdir_path.is_absolute():
                    fdir_path = resolved_repo / fdir_path
                active_feature_dir = fdir_path.resolve()
        except Exception:
            active_feature_dir = None

    if not target_clean and active_feature_dir is not None:
        return active_feature_dir

    # Search in official specs/ directory first, then legacy .specs/
    for candidate_root in (resolved_repo / "specs", resolved_repo / ".specs"):
        if not candidate_root.is_dir():
            continue
        if target_clean:
            exact = candidate_root / target_clean
            if exact.is_dir():
                return exact.resolve()
            lower_target = target_clean.lower()
            for child in sorted(candidate_root.iterdir()):
                if child.is_dir() and lower_target in child.name.lower():
                    return child.resolve()
            # Match numeric issue key suffix (e.g. FAL-53 -> 053-)
            num_match = re.search(r"(\d+)$", target_clean)
            if num_match:
                num_prefix = f"{int(num_match.group(1)):03d}-"
                for child in sorted(candidate_root.iterdir()):
                    if child.is_dir() and child.name.startswith(num_prefix):
                        return child.resolve()

    if active_feature_dir is not None and active_feature_dir.is_dir():
        if not target_clean or target_clean.lower() in active_feature_dir.name.lower():
            return active_feature_dir

    default_root = (resolved_repo / "specs") if (resolved_repo / "specs").is_dir() else (resolved_repo / ".specs")
    return (default_root / (target_clean or "unknown")).resolve()


def bootstrap_specify(
    repo_root: Optional[Path] = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Bootstrap the official github/spec-kit .specify/ runtime directory from bundled skill assets
    into the target repository root. Preserves existing constitution.md and feature.json unless force=True.
    """
    resolved_repo = (repo_root or Path.cwd()).resolve()
    assets_specify = Path(__file__).resolve().parent.parent / "assets" / ".specify"
    if not assets_specify.is_dir():
        return {
            "success": False,
            "error": f"Bundled .specify assets not found at '{assets_specify}'"
        }

    dest_specify = resolved_repo / ".specify"
    copied_files: List[str] = []
    skipped_files: List[str] = []

    for src_path in sorted(assets_specify.rglob("*")):
        rel = src_path.relative_to(assets_specify)
        dest_path = dest_specify / rel
        if src_path.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
            continue

        # Preserve existing constitution.md and feature.json unless force=True
        if not force and dest_path.is_file() and rel.as_posix() in ("memory/constitution.md", "feature.json"):
            skipped_files.append(rel.as_posix())
            continue

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest_path)
        copied_files.append(rel.as_posix())

    return {
        "success": True,
        "specify_dir": str(dest_specify),
        "copied_count": len(copied_files),
        "skipped_files": skipped_files,
    }


def validate_spec_plan(
    target: str = "",
    specs_root: Optional[Path] = None,
    repo_root: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Validate local Spec-Driven Development artifacts (specs/<feature>/plan.md or .specs/<issue-key>/plan.md and tasks.md).
    Checks mandatory sections, file path integrity, and actionable tasks checklist.
    """
    resolved_repo = (repo_root or Path.cwd()).resolve()
    spec_dir = _resolve_spec_dir(target=target, resolved_repo=resolved_repo, specs_root=specs_root)

    errors: List[str] = []
    warnings: List[str] = []

    specify_constitution = resolved_repo / ".specify" / "memory" / "constitution.md"
    legacy_constitution = resolved_repo / ".speckit" / "constitution.md"
    constitution_exists = specify_constitution.is_file() or legacy_constitution.is_file()
    if not constitution_exists:
        warnings.append("File '.specify/memory/constitution.md' not found in repository root.")

    if not spec_dir.is_dir():
        return {
            "success": False,
            "valid": False,
            "issue_dir": str(spec_dir),
            "constitution_exists": constitution_exists,
            "files": {"spec_md": False, "plan_md": False, "tasks_md": False},
            "sections_found": [],
            "impacted_files": [],
            "tasks": {"total": 0, "completed": 0, "pending": 0},
            "errors": [f"Spec directory not found: '{spec_dir}'"],
            "warnings": warnings,
        }

    spec_file = spec_dir / "spec.md"
    plan_file = spec_dir / "plan.md"
    tasks_file = spec_dir / "tasks.md"

    files_status = {
        "spec_md": spec_file.is_file(),
        "plan_md": plan_file.is_file(),
        "tasks_md": tasks_file.is_file(),
    }

    if not files_status["plan_md"]:
        errors.append(f"Missing mandatory file: '{plan_file.name}'")
    if not files_status["tasks_md"]:
        errors.append(f"Missing mandatory file: '{tasks_file.name}'")

    sections_found: List[str] = []
    impacted_files: List[str] = []

    if files_status["plan_md"]:
        plan_text = plan_file.read_text(encoding="utf-8")
        plan_lines = plan_text.splitlines()

        # Check required sections and collect lines under each section
        section_indices: Dict[str, int] = {}
        all_heading_indices: List[int] = []
        for idx, line in enumerate(plan_lines):
            if re.match(r"^#{1,4}\s+\S+", line.strip()):
                all_heading_indices.append(idx)
            for sec_name, pattern in REQUIRED_PLAN_SECTIONS:
                if sec_name not in section_indices and re.search(pattern, line.strip()):
                    section_indices[sec_name] = idx
                    sections_found.append(sec_name)

        for sec_name, _ in REQUIRED_PLAN_SECTIONS:
            if sec_name not in section_indices:
                errors.append(f"Missing required section in plan.md: '{sec_name}'")

        # Validate Checklist de Arquivos Impactados content
        if "Checklist de Arquivos Impactados" in section_indices:
            start_idx = section_indices["Checklist de Arquivos Impactados"]
            next_headings = [i for i in all_heading_indices if i > start_idx]
            end_idx = next_headings[0] if next_headings else len(plan_lines)
            checklist_lines = plan_lines[start_idx + 1 : end_idx]

            for raw_line in checklist_lines:
                stripped = raw_line.strip()
                bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
                if not bullet_match:
                    continue
                bullet_body = bullet_match.group(1).strip()
                extracted_path = _extract_file_path_from_bullet(bullet_body)
                if not extracted_path:
                    continue

                # Normalize wildcard globs like dir/* or file-*.md when checking parent/target existence
                normalized_check_path = re.sub(r"[\*\?].*$", "", extracted_path).rstrip("/\\") or "."

                # Check for placeholders or illegal characters (excluding glob *)
                if re.search(r"[<>?\"|]", extracted_path) or extracted_path in ("...", "TODO", "path/to/file"):
                    errors.append(f"Invalid placeholder or file path in plan.md checklist: '{extracted_path}'")
                    continue

                impacted_files.append(extracted_path)
                full_target = (resolved_repo / normalized_check_path).resolve()
                try:
                    full_target.relative_to(resolved_repo)
                except ValueError:
                    errors.append(f"File path escapes repository root: '{extracted_path}'")
                    continue

                is_new_file = bool(re.search(r"(?i)\b(criar|create|novo|new|add|adicionar)\b", bullet_body))
                if not is_new_file and not full_target.exists():
                    # If neither the file nor its parent directory exists, flag error
                    if not full_target.parent.exists():
                        errors.append(
                            f"Impacted file path does not exist (and is not marked as new): '{extracted_path}'"
                        )

            if not impacted_files:
                errors.append("Section 'Checklist de Arquivos Impactados' in plan.md must list at least one file path.")

    tasks_summary = {"total": 0, "completed": 0, "pending": 0}
    if files_status["tasks_md"]:
        tasks_text = tasks_file.read_text(encoding="utf-8")
        for line in tasks_text.splitlines():
            m = re.match(r"^\s*[-*]\s+\[([ xX])\]\s+(.+)$", line)
            if m:
                state_char = m.group(1)
                task_desc = m.group(2).strip()
                if re.search(r"^<[^>]+>$", task_desc) or task_desc.upper() == "TODO":
                    errors.append(f"Placeholder task item found in tasks.md: '{task_desc}'")
                tasks_summary["total"] += 1
                if state_char.lower() == "x":
                    tasks_summary["completed"] += 1
                else:
                    tasks_summary["pending"] += 1

        if tasks_summary["total"] == 0:
            errors.append("File 'tasks.md' must contain at least one actionable checkbox item ('- [ ] ...').")

    is_valid = len(errors) == 0
    return {
        "success": is_valid,
        "valid": is_valid,
        "issue_dir": str(spec_dir),
        "constitution_exists": constitution_exists,
        "files": files_status,
        "sections_found": sections_found,
        "impacted_files": impacted_files,
        "tasks": tasks_summary,
        "errors": errors,
        "warnings": warnings,
    }


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
        "description": sanitize_markdown_payload(resolved_description or "")
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

    if resolved_description is not None:
        resolved_description = sanitize_markdown_payload(resolved_description)

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

    if resolved_comment is not None:
        resolved_comment = sanitize_markdown_payload(resolved_comment)

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


def cmd_validate_plan(target: str = "", specs_root: Optional[str] = None, repo_root: Optional[str] = None):
    """Validate local Spec-Driven Development plan.md and tasks.md artifacts."""
    result = validate_spec_plan(
        target=target or "",
        specs_root=Path(specs_root) if specs_root else None,
        repo_root=Path(repo_root) if repo_root else None,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result.get("valid", False):
        sys.exit(1)


def cmd_bootstrap_specify(repo_root: Optional[str] = None, force: bool = False):
    """Bootstrap official .specify/ runtime directory from bundled assets into target repository."""
    result = bootstrap_specify(
        repo_root=Path(repo_root) if repo_root else None,
        force=force,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result.get("success", False):
        sys.exit(1)


def cmd_sanitize_markdown(input_file: str, output_file: Optional[str] = None, in_place: bool = False):
    """Sanitize a UTF-8 Markdown file deterministically."""
    src = Path(input_file)
    if not src.is_file():
        print(json.dumps({
            "success": False,
            "error": f"Input file not found: '{input_file}'"
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

    raw_text = src.read_text(encoding="utf-8")
    sanitized = sanitize_markdown_payload(raw_text)
    dest = src if in_place else (Path(output_file) if output_file else None)
    if dest is not None:
        dest.write_text(sanitized, encoding="utf-8")
        print(json.dumps({
            "success": True,
            "file": str(dest),
            "original_length": len(raw_text),
            "sanitized_length": len(sanitized)
        }, indent=2, ensure_ascii=False))
    else:
        print(sanitized, end="")


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

    # validate-plan (local static validation, no API key required)
    v_plan = subparsers.add_parser("validate-plan", help="Validate local specs/<feature>/plan.md and tasks.md integrity")
    v_plan.add_argument("target", nargs="?", default="", help="Issue key (e.g. FAL-53) or path to spec directory (optional, defaults to .specify/feature.json)")
    v_plan.add_argument("--issue-key", dest="issue_key", help="Issue key (e.g. FAL-53) or feature directory name")
    v_plan.add_argument("--specs-root", help="Custom specs root directory (defaults to <repo-root>/specs or .specs)")
    v_plan.add_argument("--repo-root", help="Repository root directory (defaults to current working directory)")

    # bootstrap-specify (local .specify/ bootstrapper, no API key required)
    b_spec = subparsers.add_parser("bootstrap-specify", help="Bootstrap official .specify/ runtime directory from bundled skill assets")
    b_spec.add_argument("--repo-root", help="Target repository root directory (defaults to current working directory)")
    b_spec.add_argument("--force", action="store_true", help="Overwrite existing .specify/memory/constitution.md and feature.json")

    # sanitize-markdown (local markdown sanitizer, no API key required)
    s_md = subparsers.add_parser("sanitize-markdown", help="Sanitize a Markdown file deterministically")
    s_md.add_argument("input_file", help="Path to UTF-8 Markdown file")
    s_md.add_argument("--output-file", help="Destination path for sanitized Markdown")
    s_md.add_argument("--in-place", action="store_true", help="Overwrite input file in place")

    args = parser.parse_args()

    if args.command == "validate-plan":
        resolved_target = args.issue_key or args.target or ""
        cmd_validate_plan(resolved_target, specs_root=args.specs_root, repo_root=args.repo_root)
        return
    elif args.command == "bootstrap-specify":
        cmd_bootstrap_specify(repo_root=args.repo_root, force=args.force)
        return
    elif args.command == "sanitize-markdown":
        cmd_sanitize_markdown(args.input_file, output_file=args.output_file, in_place=args.in_place)
        return

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
