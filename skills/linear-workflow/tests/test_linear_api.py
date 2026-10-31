import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import sys
import os
import json
import io

# Add scripts directory to sys.path
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

import linear_api

class TestLinearApiUpdateIssue(unittest.TestCase):
    @patch("linear_api.execute_graphql")
    def test_update_issue_with_description(self, mock_execute):
        # Mock GET_ISSUE_QUERY response
        mock_execute.side_effect = [
            {
                "success": True,
                "data": {
                    "issue": {
                        "id": "uuid-123",
                        "identifier": "FAL-34",
                        "title": "Test Issue",
                        "team": {"id": "team-1"},
                        "comments": {"nodes": []}
                    }
                }
            },
            # Mock UPDATE_ISSUE_MUTATION response
            {
                "success": True,
                "data": {
                    "issueUpdate": {
                        "success": True,
                        "issue": {
                            "id": "uuid-123",
                            "identifier": "FAL-34",
                            "title": "Test Issue",
                            "state": {"id": "state-1", "name": "Todo"}
                        }
                    }
                }
            }
        ]

        with patch("builtins.print") as mock_print:
            linear_api.cmd_update_issue(
                api_key="fake-key",
                issue_id="FAL-34",
                description="## Nova Especificacao Tecnica"
            )

        self.assertEqual(mock_execute.call_count, 2)
        update_call = mock_execute.call_args_list[1]
        mutation = update_call[0][1]
        variables = update_call[0][2]
        self.assertIn("mutation UpdateIssue", mutation)
        self.assertEqual(variables["id"], "uuid-123")
        self.assertEqual(variables["input"]["description"], "## Nova Especificacao Tecnica")

    @patch("linear_api.execute_graphql")
    def test_update_issue_with_description_file(self, mock_execute):
        mock_execute.side_effect = [
            {
                "success": True,
                "data": {
                    "issue": {
                        "id": "uuid-456",
                        "identifier": "FAL-34",
                        "title": "Test Issue",
                        "team": {"id": "team-1"},
                        "comments": {"nodes": []}
                    }
                }
            },
            {
                "success": True,
                "data": {
                    "issueUpdate": {
                        "success": True,
                        "issue": {
                            "id": "uuid-456",
                            "identifier": "FAL-34",
                            "title": "Test Issue"
                        }
                    }
                }
            }
        ]

        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
            tf.write("### Conteudo via Arquivo")
            tf_path = tf.name

        try:
            with patch("builtins.print"):
                linear_api.cmd_update_issue(
                    api_key="fake-key",
                    issue_id="FAL-34",
                    description_file=tf_path
                )

            self.assertEqual(mock_execute.call_count, 2)
            variables = mock_execute.call_args_list[1][0][2]
            self.assertEqual(variables["input"]["description"], "### Conteudo via Arquivo")
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)

    @patch("linear_api.resolve_state_id", return_value="state-todo-id")
    @patch("linear_api.execute_graphql")
    def test_update_issue_with_state_and_description(self, mock_execute, mock_resolve_state):
        mock_execute.side_effect = [
            {
                "success": True,
                "data": {
                    "issue": {
                        "id": "uuid-789",
                        "identifier": "FAL-34",
                        "title": "Test Issue",
                        "team": {"id": "team-1"},
                        "comments": {"nodes": []}
                    }
                }
            },
            {
                "success": True,
                "data": {
                    "issueUpdate": {
                        "success": True,
                        "issue": {
                            "id": "uuid-789",
                            "identifier": "FAL-34",
                            "title": "Test Issue"
                        }
                    }
                }
            }
        ]

        with patch("builtins.print"):
            linear_api.cmd_update_issue(
                api_key="fake-key",
                issue_id="FAL-34",
                state_name="Todo",
                description="Novo escopo atualizado"
            )

        self.assertEqual(mock_execute.call_count, 2)
        variables = mock_execute.call_args_list[1][0][2]
        self.assertEqual(variables["input"]["stateId"], "state-todo-id")
        self.assertEqual(variables["input"]["description"], "Novo escopo atualizado")

    @patch("linear_api.execute_graphql")
    def test_update_issue_with_title(self, mock_execute):
        mock_execute.side_effect = [
            {
                "success": True,
                "data": {
                    "issue": {
                        "id": "uuid-title-1",
                        "identifier": "FAL-39",
                        "title": "Old Preliminary Title",
                        "team": {"id": "team-1"},
                        "comments": {"nodes": []}
                    }
                }
            },
            {
                "success": True,
                "data": {
                    "issueUpdate": {
                        "success": True,
                        "issue": {
                            "id": "uuid-title-1",
                            "identifier": "FAL-39",
                            "title": "feat(linear-workflow): enforce mandatory card title and description update"
                        }
                    }
                }
            }
        ]

        with patch("builtins.print") as mock_print:
            linear_api.cmd_update_issue(
                api_key="fake-key",
                issue_id="FAL-39",
                title="  feat(linear-workflow): enforce mandatory card title and description update  "
            )

        self.assertEqual(mock_execute.call_count, 2)
        variables = mock_execute.call_args_list[1][0][2]
        self.assertEqual(
            variables["input"]["title"],
            "feat(linear-workflow): enforce mandatory card title and description update"
        )
        printed_payload = json.loads(mock_print.call_args[0][0])
        self.assertTrue(printed_payload["title_update"]["success"])
        self.assertTrue(printed_payload["title_update"]["updated"])
        self.assertEqual(
            printed_payload["title_update"]["title"],
            "feat(linear-workflow): enforce mandatory card title and description update"
        )
        self.assertEqual(
            printed_payload["issue"]["title"],
            "feat(linear-workflow): enforce mandatory card title and description update"
        )

    @patch("linear_api.resolve_state_id", return_value="state-todo-id")
    @patch("linear_api.execute_graphql")
    def test_update_issue_atomic_title_description_state_and_comment(self, mock_execute, mock_resolve_state):
        mock_execute.side_effect = [
            {
                "success": True,
                "data": {
                    "issue": {
                        "id": "uuid-atomic-39",
                        "identifier": "FAL-39",
                        "title": "Draft Backlog Title",
                        "team": {"id": "team-1"},
                        "comments": {"nodes": []}
                    }
                }
            },
            {
                "success": True,
                "data": {
                    "issueUpdate": {
                        "success": True,
                        "issue": {
                            "id": "uuid-atomic-39",
                            "identifier": "FAL-39",
                            "title": "feat(linear-workflow): refined title",
                            "state": {"id": "state-todo-id", "name": "Todo"}
                        }
                    }
                }
            },
            {
                "success": True,
                "data": {
                    "commentCreate": {
                        "success": True,
                        "comment": {
                            "id": "comment-uuid-39",
                            "body": "🤖 **AI Agent Update**: Análise Técnica Concluída",
                            "createdAt": "2026-10-27T00:00:00Z"
                        }
                    }
                }
            }
        ]

        with patch("builtins.print") as mock_print:
            linear_api.cmd_update_issue(
                api_key="fake-key",
                issue_id="FAL-39",
                state_name="Todo",
                title="feat(linear-workflow): refined title",
                description="### Refined Description\n- Criterion 1",
                comment="🤖 **AI Agent Update**: Análise Técnica Concluída"
            )

        self.assertEqual(mock_execute.call_count, 3)
        update_vars = mock_execute.call_args_list[1][0][2]
        self.assertEqual(update_vars["input"]["stateId"], "state-todo-id")
        self.assertEqual(update_vars["input"]["title"], "feat(linear-workflow): refined title")
        self.assertEqual(update_vars["input"]["description"], "### Refined Description\n- Criterion 1")

        comment_vars = mock_execute.call_args_list[2][0][2]
        self.assertEqual(comment_vars["input"]["issueId"], "uuid-atomic-39")

        printed_payload = json.loads(mock_print.call_args[0][0])
        self.assertTrue(printed_payload["state_update"]["success"])
        self.assertTrue(printed_payload["title_update"]["updated"])
        self.assertTrue(printed_payload["description_update"]["updated"])
        self.assertTrue(printed_payload["comment"]["created"])

    @patch("linear_api.cmd_update_issue")
    @patch("linear_api.resolve_api_key", return_value="fake-key")
    def test_cli_update_issue_parses_title_arg(self, mock_resolve_key, mock_cmd_update):
        test_argv = [
            "linear_api.py",
            "update-issue",
            "FAL-39",
            "--state", "Todo",
            "--title", "feat(linear-workflow): new title",
            "--description", "Updated body",
            "--comment", "Spec comment"
        ]
        with patch.object(sys, "argv", test_argv):
            linear_api.main()

        mock_cmd_update.assert_called_once_with(
            "fake-key",
            "FAL-39",
            team_id=None,
            state_name="Todo",
            comment="Spec comment",
            force_comment=False,
            description="Updated body",
            description_file=None,
            title="feat(linear-workflow): new title",
            comment_file=None
        )

    @patch("linear_api.resolve_or_create_label_id", return_value="label-feature-id")
    @patch("linear_api.resolve_state_id", return_value="state-backlog-id")
    @patch("linear_api.execute_graphql")
    def test_create_issue_with_feature_label(self, mock_execute, mock_resolve_state, mock_resolve_label):
        mock_execute.return_value = {
            "success": True,
            "data": {
                "issueCreate": {
                    "success": True,
                    "issue": {
                        "id": "uuid-new-1",
                        "identifier": "FAL-32",
                        "title": "fix(skills): garantir exibicao do plano",
                        "labels": {"nodes": [{"id": "label-feature-id", "name": "Feature"}]}
                    }
                }
            }
        }

        with patch("builtins.print"):
            linear_api.cmd_create_issue(
                api_key="fake-key",
                team_id="team-1",
                title="fix(skills): garantir exibicao do plano",
                description="Descricao detalhada",
                project_id="proj-1",
                state_name="Backlog",
                labels=["Feature"]
            )

        mock_resolve_label.assert_called_once_with("fake-key", "team-1", "Feature")
        variables = mock_execute.call_args[0][2]
        self.assertEqual(variables["input"]["labelIds"], ["label-feature-id"])
        self.assertEqual(variables["input"]["stateId"], "state-backlog-id")

    @patch("linear_api.resolve_state_id", return_value="state-backlog-id")
    @patch("linear_api.execute_graphql")
    def test_create_issue_without_labels(self, mock_execute, mock_resolve_state):
        mock_execute.return_value = {
            "success": True,
            "data": {
                "issueCreate": {
                    "success": True,
                    "issue": {
                        "id": "uuid-new-2",
                        "identifier": "FAL-35",
                        "title": "chore(skills): atualizar documentacao",
                        "labels": {"nodes": []}
                    }
                }
            }
        }

        with patch("builtins.print"):
            linear_api.cmd_create_issue(
                api_key="fake-key",
                team_id="team-1",
                title="chore(skills): atualizar documentacao",
                description="Sem label de componente",
                project_id="proj-1",
                state_name="Backlog",
                labels=None
            )

        variables = mock_execute.call_args[0][2]
        self.assertNotIn("labelIds", variables["input"])
        self.assertEqual(variables["input"]["stateId"], "state-backlog-id")

    def test_skill_files_enforce_prerender_and_tooling_labels(self):
        skill_root = Path(__file__).resolve().parent.parent
        speckit_specify = (skill_root / ".apm" / "skills" / "speckit-specify" / "SKILL.md").read_text(encoding="utf-8")
        speckit_tasks = (skill_root / ".apm" / "skills" / "speckit-tasks" / "SKILL.md").read_text(encoding="utf-8")
        main_skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Proibição de Consent Gate Cego", main_skill)
        for content in (speckit_specify, speckit_tasks, main_skill):
            self.assertIn("Pre-Render Gate", content)

        self.assertIn("Feature", speckit_specify)
        self.assertIn("Feature", main_skill)
        self.assertIn("não force `Back`", main_skill)

    def test_skill_files_enforce_mandatory_title_and_description_in_tech_analysis(self):
        skill_root = Path(__file__).resolve().parent.parent
        speckit_plan = (skill_root / ".apm" / "skills" / "speckit-plan" / "SKILL.md").read_text(encoding="utf-8")
        speckit_tasks = (skill_root / ".apm" / "skills" / "speckit-tasks" / "SKILL.md").read_text(encoding="utf-8")
        speckit_tasks_prompt = (skill_root / ".apm" / "prompts" / "speckit-tasks.prompt.md").read_text(encoding="utf-8")
        instructions = (skill_root / ".apm" / "instructions" / "linear-lifecycle-commands.instructions.md").read_text(encoding="utf-8")
        main_skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        multi_harness = (skill_root / "references" / "multi-harness-commands.md").read_text(encoding="utf-8")
        states_ref = (skill_root / "references" / "states-and-labels.md").read_text(encoding="utf-8")

        for content in (speckit_plan, speckit_tasks, speckit_tasks_prompt, instructions, main_skill):
            self.assertIn("Título Revisado", content)
            self.assertIn("Descrição Atualizada", content)
            self.assertIn("--title", content)
            self.assertIn("--description-file", content)

        self.assertIn("Título Revisado", multi_harness)
        self.assertIn("--description-file", states_ref)

    @patch("linear_api.resolve_state_id", return_value="state-backlog-id")
    @patch("linear_api.execute_graphql")
    def test_create_issue_with_description_file(self, mock_execute, mock_resolve_state):
        mock_execute.return_value = {
            "success": True,
            "data": {
                "issueCreate": {
                    "success": True,
                    "issue": {
                        "id": "uuid-new-40",
                        "identifier": "FAL-40",
                        "title": "fix(workflows): prevent shell backtick corruption"
                    }
                }
            }
        }

        markdown_body = (
            "### Type of Change\n"
            "- [x] `feat`: New feature\n"
            "- [ ] `fix`: Bug fix\n"
            "- [ ] `test`: Test suite update\n"
            "- [ ] `refactor`: Code refactoring\n"
            "- [ ] `chore`: Maintenance\n"
            'Example with "double quotes" and `backticks`.'
        )
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
            tf.write(markdown_body)
            tf_path = tf.name

        try:
            with patch("builtins.print"):
                linear_api.cmd_create_issue(
                    api_key="fake-key",
                    team_id="team-1",
                    title="fix(workflows): prevent shell backtick corruption",
                    project_id="proj-1",
                    state_name="Backlog",
                    description_file=tf_path
                )

            variables = mock_execute.call_args[0][2]
            self.assertEqual(variables["input"]["description"], markdown_body)
            self.assertIn("`feat`", variables["input"]["description"])
            self.assertIn("`fix`", variables["input"]["description"])
            self.assertIn("`test`", variables["input"]["description"])
            self.assertIn("`refactor`", variables["input"]["description"])
            self.assertIn("`chore`", variables["input"]["description"])
            self.assertIn('"double quotes"', variables["input"]["description"])
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)

    @patch("linear_api.execute_graphql")
    def test_update_issue_with_comment_file(self, mock_execute):
        mock_execute.side_effect = [
            {
                "success": True,
                "data": {
                    "issue": {
                        "id": "uuid-40",
                        "identifier": "FAL-40",
                        "title": "Test Issue",
                        "team": {"id": "team-1"},
                        "comments": {"nodes": []}
                    }
                }
            },
            {
                "success": True,
                "data": {
                    "commentCreate": {
                        "success": True,
                        "comment": {
                            "id": "comment-uuid-40",
                            "body": "🤖 **AI Agent Update**: Tested `feat`, `fix`, `test`, `refactor`, `chore` with \"quotes\".",
                            "createdAt": "2026-10-27T01:00:00Z"
                        }
                    }
                }
            }
        ]

        comment_markdown = '🤖 **AI Agent Update**: Tested `feat`, `fix`, `test`, `refactor`, `chore` with "quotes".'
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tf:
            tf.write(comment_markdown)
            tf_path = tf.name

        try:
            with patch("builtins.print") as mock_print:
                linear_api.cmd_update_issue(
                    api_key="fake-key",
                    issue_id="FAL-40",
                    comment_file=tf_path
                )

            self.assertEqual(mock_execute.call_count, 2)
            comment_vars = mock_execute.call_args_list[1][0][2]
            self.assertEqual(comment_vars["input"]["body"], comment_markdown)
            printed_payload = json.loads(mock_print.call_args[0][0])
            self.assertTrue(printed_payload["comment"]["created"])
        finally:
            if os.path.exists(tf_path):
                os.remove(tf_path)

    @patch("linear_api.cmd_update_issue")
    def test_create_comment_with_comment_file(self, mock_cmd_update):
        linear_api.cmd_create_comment(
            api_key="fake-key",
            issue_id="FAL-40",
            comment=None,
            force=True,
            comment_file="comment.md"
        )
        mock_cmd_update.assert_called_once_with(
            "fake-key",
            issue_id="FAL-40",
            comment=None,
            comment_file="comment.md",
            force_comment=True
        )

    @patch("linear_api.cmd_create_comment")
    @patch("linear_api.cmd_update_issue")
    @patch("linear_api.cmd_create_issue")
    @patch("linear_api.resolve_api_key", return_value="fake-key")
    def test_cli_parses_file_arguments(self, mock_resolve_key, mock_create_issue, mock_update_issue, mock_create_comment):
        with patch.object(sys, "argv", [
            "linear_api.py", "create-issue",
            "--team-id", "team-1",
            "--title", "fix(workflows): title",
            "--description-file", "desc.md",
            "--state", "Backlog"
        ]):
            linear_api.main()
        mock_create_issue.assert_called_once_with(
            "fake-key", "team-1", "fix(workflows): title", "", None, "Backlog", None, description_file="desc.md"
        )

        with patch.object(sys, "argv", [
            "linear_api.py", "update-issue", "FAL-40",
            "--state", "In Review",
            "--description-file", "desc.md",
            "--comment-file", "comment.md"
        ]):
            linear_api.main()
        mock_update_issue.assert_called_once_with(
            "fake-key", "FAL-40",
            team_id=None,
            state_name="In Review",
            comment=None,
            force_comment=False,
            description=None,
            description_file="desc.md",
            title=None,
            comment_file="comment.md"
        )

        with patch.object(sys, "argv", [
            "linear_api.py", "create-comment", "FAL-40",
            "--comment-file", "comment.md"
        ]):
            linear_api.main()
        mock_create_comment.assert_called_once_with(
            "fake-key", "FAL-40", None, False, comment_file="comment.md"
        )

    def test_skill_files_enforce_markdown_file_payloads(self):
        skill_root = Path(__file__).resolve().parent.parent
        repo_root = skill_root.parent.parent

        git_skill = (repo_root / "skills" / "git-workflow" / "SKILL.md").read_text(encoding="utf-8")
        gitflow_ref = (repo_root / "skills" / "git-workflow" / "references" / "gitflow.md").read_text(encoding="utf-8")
        linear_skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        speckit_specify = (skill_root / ".apm" / "skills" / "speckit-specify" / "SKILL.md").read_text(encoding="utf-8")
        speckit_tasks = (skill_root / ".apm" / "skills" / "speckit-tasks" / "SKILL.md").read_text(encoding="utf-8")
        speckit_implement = (skill_root / ".apm" / "skills" / "speckit-implement" / "SKILL.md").read_text(encoding="utf-8")
        speckit_converge = (skill_root / ".apm" / "skills" / "speckit-converge" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("--body-file", git_skill)
        self.assertIn("--body-file", gitflow_ref)
        self.assertIn("--description-file", linear_skill)
        self.assertIn("--comment-file", linear_skill)
        self.assertIn("--body-file", linear_skill)
        self.assertIn("--description-file", speckit_specify)
        self.assertIn("--description-file", speckit_tasks)
        self.assertIn("--comment-file", speckit_tasks)
        self.assertIn("--comment-file", speckit_implement)
        self.assertIn("--body-file", speckit_implement)
        self.assertIn("--comment-file", speckit_converge)
        self.assertIn("--body-file", speckit_converge)

    def test_sanitize_markdown_payload_closes_unclosed_code_blocks(self):
        raw = (
            "### Exemplo de Código\n"
            "```python\n"
            "def hello():\n"
            "    return 'world'"
        )
        sanitized = linear_api.sanitize_markdown_payload(raw)
        self.assertTrue(sanitized.endswith("\n```"))
        self.assertEqual(sanitized.count("```"), 2)

        # Already closed fence should not duplicate closing fence
        already_closed = "```bash\necho ok\n```"
        self.assertEqual(linear_api.sanitize_markdown_payload(already_closed), already_closed)

    def test_sanitize_markdown_payload_aligns_misaligned_tables(self):
        raw = (
            "Resumo da análise (FAL-53): teste | Arquivos: 3 | Branch: feat/FAL-53\n\n"
            "| Arquivo | Ação | Status |\n"
            "| :--- |---\n"
            "| linear_api.py | Modificar\n"
            "SKILL.md | Atualizar | OK |"
        )
        sanitized = linear_api.sanitize_markdown_payload(raw)
        lines = sanitized.split("\n")
        # Single-line prose with pipes must remain untouched
        self.assertEqual(
            lines[0],
            "Resumo da análise (FAL-53): teste | Arquivos: 3 | Branch: feat/FAL-53"
        )
        # Table rows must all have aligned leading/trailing pipes and 3 columns
        self.assertEqual(lines[2], "| Arquivo | Ação | Status |")
        self.assertEqual(lines[3], "| :--- | --- | --- |")
        self.assertEqual(lines[4], "| linear_api.py | Modificar |  |")
        self.assertEqual(lines[5], "| SKILL.md | Atualizar | OK |")

    def test_sanitize_markdown_payload_strips_control_chars_and_crlf(self):
        raw = "Linha 1\r\nLinha 2\rLinha 3 com \x0cformfeed e \x08backspace e \x00null\tcom tab"
        sanitized = linear_api.sanitize_markdown_payload(raw)
        self.assertNotIn("\r", sanitized)
        self.assertNotIn("\x0c", sanitized)
        self.assertNotIn("\x08", sanitized)
        self.assertNotIn("\x00", sanitized)
        self.assertEqual(
            sanitized,
            "Linha 1\nLinha 2\nLinha 3 com formfeed e backspace e null\tcom tab"
        )

    def test_validate_spec_plan_valid_and_invalid_cases(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / ".speckit").mkdir(parents=True)
            (repo_root / ".speckit" / "constitution.md").write_text("# Constitution\n", encoding="utf-8")
            (repo_root / "src").mkdir(parents=True)
            (repo_root / "src" / "existing.py").write_text("print(1)\n", encoding="utf-8")

            spec_dir = repo_root / ".specs" / "FAL-99"
            spec_dir.mkdir(parents=True)
            (spec_dir / "plan.md").write_text(
                "# Plano FAL-99\n\n"
                "## 1. Diagnóstico e Contexto\nContexto ok.\n\n"
                "## 2. Arquitetura da Solução & Desenho Técnico\nDesign ok.\n\n"
                "## 3. Checklist de Arquivos Impactados\n"
                "- `src/existing.py` (modificar)\n"
                "- `src/new_module.py` (criar)\n\n"
                "## 4. Estratégia de Testes\n`python -m unittest`\n\n"
                "## 5. Plano Gitflow\n- Branch: `feat/FAL-99-test`\n",
                encoding="utf-8"
            )
            (spec_dir / "tasks.md").write_text(
                "# Tasks\n- [x] Task 1\n- [ ] Task 2\n",
                encoding="utf-8"
            )

            res = linear_api.validate_spec_plan("FAL-99", repo_root=repo_root)
            self.assertTrue(res["valid"])
            self.assertEqual(len(res["sections_found"]), 5)
            self.assertEqual(res["tasks"]["total"], 2)
            self.assertEqual(res["tasks"]["completed"], 1)
            self.assertEqual(res["tasks"]["pending"], 1)

            # Invalid case: missing section and placeholder file path
            bad_dir = repo_root / ".specs" / "FAL-100"
            bad_dir.mkdir(parents=True)
            (bad_dir / "plan.md").write_text(
                "# Plano Incompleto\n\n"
                "## 1. Diagnóstico e Contexto\nOk\n\n"
                "## 3. Checklist de Arquivos Impactados\n"
                "- `<arquivo-1>`\n"
                "- `nonexistent_dir/missing.py` (modificar)\n",
                encoding="utf-8"
            )
            (bad_dir / "tasks.md").write_text("# Sem checkboxes\nTexto solto\n", encoding="utf-8")

            bad_res = linear_api.validate_spec_plan("FAL-100", repo_root=repo_root)
            self.assertFalse(bad_res["valid"])
            self.assertTrue(any("Arquitetura da Solução" in e for e in bad_res["errors"]))
            self.assertTrue(any("<arquivo-1>" in e for e in bad_res["errors"]))
            self.assertTrue(any("nonexistent_dir/missing.py" in e for e in bad_res["errors"]))
            self.assertTrue(any("tasks.md" in e for e in bad_res["errors"]))

    def test_validate_fal53_homologation_spec_and_sdd_skill_contracts(self):
        skill_root = Path(__file__).resolve().parent.parent
        repo_root = skill_root.parent.parent

        # Validate real FAL-53 spec artifacts in specs/053-fal-53-spec-kit-linear-workflow
        res = linear_api.validate_spec_plan("FAL-53", repo_root=repo_root)
        self.assertTrue(res["valid"], f"Expected FAL-53 spec to be valid, got errors: {res['errors']}")
        self.assertTrue(res["constitution_exists"])
        self.assertTrue(res["files"]["spec_md"])
        self.assertTrue(res["files"]["plan_md"])
        self.assertTrue(res["files"]["tasks_md"])

        # Verify official github/spec-kit & Executive Briefing contracts in skill files
        linear_skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        speckit_plan = (skill_root / ".apm" / "skills" / "speckit-plan" / "SKILL.md").read_text(encoding="utf-8")
        speckit_tasks = (skill_root / ".apm" / "skills" / "speckit-tasks" / "SKILL.md").read_text(encoding="utf-8")
        speckit_impl = (skill_root / ".apm" / "skills" / "speckit-implement" / "SKILL.md").read_text(encoding="utf-8")
        speckit_spec = (skill_root / ".apm" / "skills" / "speckit-specify" / "SKILL.md").read_text(encoding="utf-8")
        instructions = (skill_root / ".apm" / "instructions" / "linear-lifecycle-commands.instructions.md").read_text(encoding="utf-8")

        self.assertIn(".specify/memory/constitution.md", linear_skill)
        self.assertIn("validate-plan", linear_skill)
        self.assertIn("sanitize_markdown_payload", linear_skill)
        self.assertIn("Executive Briefing", speckit_plan)
        self.assertIn("Executive Briefing", speckit_tasks)
        self.assertIn("validate-plan", speckit_tasks)
        self.assertIn("In Progress", speckit_impl)
        self.assertIn("In Review", speckit_impl)
        self.assertIn("Backlog", speckit_spec)
        self.assertIn("validate-plan", instructions)

    def test_bootstrap_specify_and_10_speckit_skills(self):
        skill_root = Path(__file__).resolve().parent.parent
        repo_root = skill_root.parent.parent

        expected_skills = [
            "speckit-analyze",
            "speckit-checklist",
            "speckit-clarify",
            "speckit-constitution",
            "speckit-converge",
            "speckit-implement",
            "speckit-plan",
            "speckit-specify",
            "speckit-tasks",
            "speckit-taskstoissues",
        ]
        for sname in expected_skills:
            self.assertTrue(
                (skill_root / ".apm" / "skills" / sname / "SKILL.md").is_file(),
                f"Missing {sname}/SKILL.md in skills/linear-workflow/.apm/skills/"
            )
            self.assertTrue(
                (skill_root / ".apm" / "prompts" / f"{sname}.prompt.md").is_file(),
                f"Missing {sname}.prompt.md in skills/linear-workflow/.apm/prompts/"
            )
            self.assertTrue(
                (repo_root / ".agents" / "skills" / sname / "SKILL.md").is_file(),
                f"Missing deployed {sname}/SKILL.md in .agents/skills/"
            )

        # Verify legacy fk-* skills are removed from linear-workflow
        for legacy in ("fk-new-issue", "fk-technical-analysis", "fk-develop", "fk-fix"):
            self.assertFalse((skill_root / ".apm" / "skills" / legacy).exists())
            self.assertFalse((repo_root / ".agents" / "skills" / legacy).exists())

        # Test bootstrap_specify in a clean temporary consumer repo
        with tempfile.TemporaryDirectory() as tmpdir:
            consumer_root = Path(tmpdir)
            boot_res = linear_api.bootstrap_specify(repo_root=consumer_root, force=False)
            self.assertTrue(boot_res["success"])
            self.assertTrue((consumer_root / ".specify" / "scripts" / "python" / "check_prerequisites.py").is_file())
            self.assertTrue((consumer_root / ".specify" / "templates" / "spec-template.md").is_file())
            self.assertTrue((consumer_root / ".specify" / "memory" / "constitution.md").is_file())

            # Modify constitution.md and ensure bootstrap_specify(force=False) preserves it
            custom_constitution = "# Custom Consumer Constitution\n"
            (consumer_root / ".specify" / "memory" / "constitution.md").write_text(custom_constitution, encoding="utf-8")
            boot_res_2 = linear_api.bootstrap_specify(repo_root=consumer_root, force=False)
            self.assertTrue(boot_res_2["success"])
            self.assertIn("memory/constitution.md", boot_res_2["skipped_files"])
            self.assertEqual(
                (consumer_root / ".specify" / "memory" / "constitution.md").read_text(encoding="utf-8"),
                custom_constitution
            )


class TestLinearWorkflowStatesAndConstants(unittest.TestCase):
    def test_canonical_workflow_states_structure(self):
        self.assertEqual(len(linear_api.CANONICAL_WORKFLOW_STATES), 7)
        state_names = [s["name"] for s in linear_api.CANONICAL_WORKFLOW_STATES]
        self.assertEqual(state_names, ["Backlog", "Planned", "Todo", "In Progress", "In Review", "Done", "Canceled"])
        for state in linear_api.CANONICAL_WORKFLOW_STATES:
            valid, errors = linear_api.validate_linear_workflow_state(state)
            self.assertTrue(valid, f"State {state['name']} failed validation: {errors}")

    def test_validate_card_id(self):
        self.assertTrue(linear_api.validate_card_id("FAL-58"))
        self.assertTrue(linear_api.validate_card_id("ABC-1234"))
        self.assertFalse(linear_api.validate_card_id("fal-58"))
        self.assertFalse(linear_api.validate_card_id("123"))
        self.assertFalse(linear_api.validate_card_id("<CARD-ID>"))
        self.assertFalse(linear_api.validate_card_id(""))
        self.assertFalse(linear_api.validate_card_id(None))

    def test_validate_linear_workflow_state_invalid(self):
        # Invalid name
        valid, errors = linear_api.validate_linear_workflow_state({
            "name": "InvalidState", "type": "unstarted", "position": 1.0, "color": "#123456"
        })
        self.assertFalse(valid)
        self.assertTrue(any("name: Um de:" in e for e in errors))

        # Invalid type
        valid, errors = linear_api.validate_linear_workflow_state({
            "name": "Planned", "type": "unknown_type", "position": 1.0, "color": "#123456"
        })
        self.assertFalse(valid)
        self.assertTrue(any("type: Um de:" in e for e in errors))

        # Invalid position
        valid, errors = linear_api.validate_linear_workflow_state({
            "name": "Planned", "type": "unstarted", "position": 99.0, "color": "#123456"
        })
        self.assertFalse(valid)
        self.assertTrue(any("position: Valores de 0.0 a 6.0" in e for e in errors))

        # Invalid color
        valid, errors = linear_api.validate_linear_workflow_state({
            "name": "Planned", "type": "unstarted", "position": 1.0, "color": "blue"
        })
        self.assertFalse(valid)
        self.assertTrue(any("color: Regex:" in e for e in errors))


class TestEphemeralWorktreeContext(unittest.TestCase):
    def test_worktree_invalid_card_id(self):
        with self.assertRaises(ValueError) as ctx:
            linear_api.EphemeralWorktreeContext("invalid-id")
        self.assertIn("Uso obrigatório: <CARD-ID>", str(ctx.exception))

    def test_worktree_lifecycle_and_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            with linear_api.EphemeralWorktreeContext("FAL-58", repo_root=repo_root) as ctx:
                self.assertEqual(ctx.status, "active")
                self.assertEqual(ctx.worktree_path, repo_root / ".worktrees" / "FAL-58")
            self.assertEqual(ctx.status, "cleaned_up")

    def test_create_and_cleanup_helpers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            ctx = linear_api.create_ephemeral_worktree("FAL-58", repo_root=repo_root)
            self.assertEqual(ctx.status, "active")
            res = linear_api.cleanup_ephemeral_worktree(ctx, repo_root=repo_root)
            self.assertTrue(res)
            self.assertEqual(ctx.status, "cleaned_up")


class TestDoneTransitionRejection(unittest.TestCase):
    def test_update_issue_blocks_done(self):
        with patch("builtins.print") as mock_print:
            res = linear_api.cmd_update_issue("fake-key", "FAL-58", state_name="Done")
            self.assertFalse(res["success"])
            self.assertEqual(
                res["error"],
                "Transição para 'Done' é restrita a humanos após merge manual de Pull Request."
            )

    def test_update_issue_blocks_done_case_insensitive(self):
        with patch("builtins.print"):
            res = linear_api.cmd_update_issue("fake-key", "FAL-58", state_name="done")
            self.assertFalse(res["success"])


class TestLivingSpecDraftPR(unittest.TestCase):
    def test_parse_draft_pr_url(self):
        raw_url = "https://github.com/CaioCoelhoChaves/fk_apm/pull/20"
        self.assertEqual(linear_api.parse_draft_pr_url(raw_url), raw_url)

        markdown_body = "* **Pull Request (Draft)**: [#20 — feat](https://github.com/CaioCoelhoChaves/fk_apm/pull/20)"
        self.assertEqual(linear_api.parse_draft_pr_url(markdown_body), raw_url)

        self.assertIsNone(linear_api.parse_draft_pr_url("No URL here"))

    @patch("subprocess.run")
    def test_create_draft_pr(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="https://github.com/CaioCoelhoChaves/fk_apm/pull/25\n",
            stderr=""
        )
        res = linear_api.create_draft_pr(
            branch_name="feat/FAL-58-modernizar",
            title="feat(FAL-58): modernizar linear-workflow",
            body="## Body text",
            base_branch="develop",
            is_draft=True
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["url"], "https://github.com/CaioCoelhoChaves/fk_apm/pull/25")
        self.assertTrue(res["is_draft"])


class TestPlannedStateResolutionAndSpecDir(unittest.TestCase):
    @patch("linear_api.execute_graphql")
    def test_resolve_state_id_planned(self, mock_execute):
        mock_execute.return_value = {
            "success": True,
            "data": {
                "team": {
                    "id": "team-1",
                    "name": "FallKey",
                    "states": {
                        "nodes": [
                            {"id": "s-backlog", "name": "Backlog"},
                            {"id": "s-planned", "name": "Planned"},
                            {"id": "s-todo", "name": "Todo"}
                        ]
                    },
                    "labels": {"nodes": []}
                }
            }
        }
        state_id = linear_api.resolve_state_id("fake-key", "team-1", "Planned")
        self.assertEqual(state_id, "s-planned")

        alias_id = linear_api.resolve_state_id("fake-key", "team-1", "planejado")
        self.assertEqual(alias_id, "s-planned")

    def test_validate_plan_with_card_id_resolution(self):
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        res = linear_api.validate_spec_plan("FAL-58", repo_root=repo_root)
        self.assertTrue(res["valid"], f"Validation failed with errors: {res.get('errors')}")
        self.assertTrue(res["files"]["spec_md"])
        self.assertTrue(res["files"]["plan_md"])
        self.assertTrue(res["files"]["tasks_md"])


class TestBoardSyncAndSetup(unittest.TestCase):
    @patch("linear_api.execute_graphql")
    def test_sync_boards_dry_run(self, mock_execute):
        mock_execute.return_value = {
            "success": True,
            "data": {
                "teams": {
                    "nodes": [
                        {
                            "id": "team-uuid-1",
                            "name": "FallKey",
                            "key": "FAL",
                            "states": {
                                "nodes": [
                                    {"id": "s1", "name": "Backlog", "type": "backlog", "position": 0.0, "color": "#BEC2C8"},
                                    {"id": "s2", "name": "Technical Analysis", "type": "unstarted", "position": 1.0, "color": "#F2C94C"},
                                    {"id": "s3", "name": "Todo", "type": "unstarted", "position": 2.0, "color": "#4EA7FC"}
                                ]
                            }
                        }
                    ]
                }
            }
        }

        with patch("builtins.print") as mock_print:
            linear_api.cmd_sync_boards("fake-key", team_id="team-uuid-1", dry_run=True)
            self.assertEqual(mock_execute.call_count, 1)

            call_args = mock_print.call_args[0][0]
            data = json.loads(call_args)
            self.assertTrue(data["success"])
            self.assertTrue(data["dry_run"])
            res = data["results"][0]
            self.assertEqual(len(res["states_updated"]), 1)
            self.assertEqual(res["states_updated"][0]["new_name"], "Planned")
            self.assertEqual(res["states_updated"][0]["previous_name"], "Technical Analysis")

    @patch("linear_api.execute_graphql")
    def test_setup_board_idempotency(self, mock_execute):
        mock_execute.side_effect = [
            {
                "success": True,
                "data": {
                    "team": {
                        "id": "team-uuid-1",
                        "states": {
                            "nodes": [
                                {"id": "s1", "name": "Backlog", "type": "backlog", "position": 0.0, "color": "#BEC2C8"},
                                {"id": "s2", "name": "Planned", "type": "unstarted", "position": 1.0, "color": "#F2C94C"}
                            ]
                        }
                    }
                }
            },
            {"success": True, "data": {"workflowStateCreate": {"workflowState": {"id": "s-new"}}}}
        ] * 10

        with patch("builtins.print") as mock_print:
            linear_api.cmd_setup_board("fake-key", team_id="team-uuid-1", force=False)
            call_args = mock_print.call_args[0][0]
            data = json.loads(call_args)
            self.assertTrue(data["success"])
            provisioned = data["provisioned_states"]
            self.assertTrue(any(p["name"] == "Backlog" and p["status"] == "existing" for p in provisioned))
            self.assertTrue(any(p["name"] == "Planned" and p["status"] == "existing" for p in provisioned))
            self.assertTrue(any(p["name"] == "Todo" and p["status"] == "created" for p in provisioned))


class TestReviewResolutionAndCommentDeduplication(unittest.TestCase):
    def test_comment_idempotency_window(self):
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        recent_time = (now - timedelta(minutes=5)).isoformat()
        old_time = (now - timedelta(minutes=20)).isoformat()

        comments = [
            {"id": "c1", "body": "Same comment body", "createdAt": recent_time},
            {"id": "c2", "body": "Old comment body", "createdAt": old_time}
        ]

        is_dup, node = linear_api.check_comment_idempotency(comments, "Same comment body", window_minutes=10.0)
        self.assertTrue(is_dup)
        self.assertEqual(node["id"], "c1")

        is_dup, node = linear_api.check_comment_idempotency(comments, "Old comment body", window_minutes=10.0)
        self.assertFalse(is_dup)

        is_dup, node = linear_api.check_comment_idempotency(comments, "Completely new", window_minutes=10.0)
        self.assertFalse(is_dup)


class TestLinearApiCreateManualIssues(unittest.TestCase):
    @patch("linear_api.execute_graphql")
    @patch("linear_api.resolve_state_id")
    @patch("linear_api.resolve_or_create_label_id")
    def test_create_manual_issues_single(self, mock_resolve_label, mock_resolve_state, mock_execute):
        mock_resolve_state.return_value = "state-backlog-id"
        mock_resolve_label.return_value = "label-manual-id"
        mock_execute.return_value = {
            "success": True,
            "data": {
                "issueCreate": {
                    "success": True,
                    "issue": {
                        "id": "uuid-man-1",
                        "identifier": "FAL-60",
                        "title": "Configurar credenciais no Gateway",
                        "url": "https://linear.app/fallkey/issue/FAL-60/configurar-credenciais",
                        "state": {"id": "state-backlog-id", "name": "Backlog"},
                        "labels": {"nodes": [{"id": "label-manual-id", "name": "manual"}]}
                    }
                }
            }
        }

        with patch("builtins.print") as mock_print:
            res = linear_api.cmd_create_manual_issues(
                api_key="fake-key",
                team_id="team-1",
                title="Configurar credenciais no Gateway",
                description="## Contexto\nAcessar dashboard",
                priority=2
            )

        self.assertTrue(res["success"])
        self.assertEqual(res["count"], 1)
        self.assertEqual(res["issues"][0]["identifier"], "FAL-60")
        self.assertEqual(res["issues"][0]["state"], "Backlog")
        self.assertIn("manual", res["issues"][0]["labels"])
        mock_resolve_state.assert_called_with("fake-key", "team-1", "Backlog")
        mock_resolve_label.assert_called_with("fake-key", "team-1", "manual")

    @patch("linear_api.execute_graphql")
    @patch("linear_api.resolve_state_id")
    @patch("linear_api.resolve_or_create_label_id")
    def test_create_manual_issues_ensures_backlog_state(self, mock_resolve_label, mock_resolve_state, mock_execute):
        mock_resolve_state.return_value = "state-backlog-uuid-99"
        mock_resolve_label.return_value = "label-manual-uuid"
        mock_execute.return_value = {
            "success": True,
            "data": {
                "issueCreate": {
                    "success": True,
                    "issue": {
                        "id": "uuid-man-2",
                        "identifier": "FAL-61",
                        "title": "Tarefa Backlog State",
                        "url": "https://linear.app/fallkey/issue/FAL-61/tarefa",
                        "state": {"id": "state-backlog-uuid-99", "name": "Backlog"},
                        "labels": {"nodes": [{"id": "label-manual-uuid", "name": "manual"}]}
                    }
                }
            }
        }

        with patch("builtins.print"):
            linear_api.cmd_create_manual_issues(
                api_key="fake-key",
                team_id="team-1",
                title="Tarefa Backlog State"
            )

        mock_resolve_state.assert_called_with("fake-key", "team-1", "Backlog")
        variables = mock_execute.call_args[0][2]
        self.assertEqual(variables["input"]["stateId"], "state-backlog-uuid-99")

    @patch("linear_api.execute_graphql")
    @patch("linear_api.resolve_state_id")
    @patch("linear_api.resolve_or_create_label_id")
    def test_create_manual_issues_ensures_manual_label(self, mock_resolve_label, mock_resolve_state, mock_execute):
        mock_resolve_state.return_value = "state-backlog-id"
        mock_resolve_label.return_value = "label-manual-id"
        mock_execute.return_value = {
            "success": True,
            "data": {
                "issueCreate": {
                    "success": True,
                    "issue": {
                        "id": "uuid-man-3",
                        "identifier": "FAL-62",
                        "title": "Verificar Manual Label",
                        "url": "https://linear.app/fallkey/issue/FAL-62/verificar",
                        "state": {"id": "state-backlog-id", "name": "Backlog"},
                        "labels": {"nodes": [{"id": "label-manual-id", "name": "manual"}]}
                    }
                }
            }
        }

        with patch("builtins.print"):
            linear_api.cmd_create_manual_issues(
                api_key="fake-key",
                team_id="team-1",
                title="Verificar Manual Label"
            )

        mock_resolve_label.assert_called_with("fake-key", "team-1", "manual")
        variables = mock_execute.call_args[0][2]
        self.assertEqual(variables["input"]["labelIds"], ["label-manual-id"])

    @patch("linear_api.execute_graphql")
    @patch("linear_api.resolve_state_id")
    @patch("linear_api.resolve_or_create_label_id")
    def test_create_manual_issues_batch(self, mock_resolve_label, mock_resolve_state, mock_execute):
        mock_resolve_state.return_value = "state-backlog-id"
        mock_resolve_label.return_value = "label-manual-id"
        mock_execute.side_effect = [
            {
                "success": True,
                "data": {
                    "issueCreate": {
                        "success": True,
                        "issue": {
                            "id": "uuid-batch-1",
                            "identifier": "FAL-71",
                            "title": "Batch Issue 1",
                            "url": "https://linear.app/fallkey/issue/FAL-71",
                            "state": {"name": "Backlog"},
                            "labels": {"nodes": [{"name": "manual"}]}
                        }
                    }
                }
            },
            {
                "success": True,
                "data": {
                    "issueCreate": {
                        "success": True,
                        "issue": {
                            "id": "uuid-batch-2",
                            "identifier": "FAL-72",
                            "title": "Batch Issue 2",
                            "url": "https://linear.app/fallkey/issue/FAL-72",
                            "state": {"name": "Backlog"},
                            "labels": {"nodes": [{"name": "manual"}]}
                        }
                    }
                }
            }
        ]

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".json") as f:
            batch_payload = {
                "issues": [
                    {"title": "Batch Issue 1", "description": "Desc 1"},
                    {"title": "Batch Issue 2", "description": "Desc 2"}
                ]
            }
            json.dump(batch_payload, f)
            batch_path = f.name

        try:
            with patch("builtins.print"):
                res = linear_api.cmd_create_manual_issues(
                    api_key="fake-key",
                    team_id="team-1",
                    batch_file=batch_path
                )
            self.assertTrue(res["success"])
            self.assertEqual(res["count"], 2)
            self.assertEqual(len(res["issues"]), 2)
            self.assertEqual(res["issues"][0]["identifier"], "FAL-71")
            self.assertEqual(res["issues"][1]["identifier"], "FAL-72")
            self.assertEqual(mock_execute.call_count, 2)
        finally:
            if os.path.exists(batch_path):
                os.remove(batch_path)

    @patch("linear_api.execute_graphql")
    def test_create_manual_issues_missing_team_or_auth(self, mock_execute):
        mock_execute.return_value = {
            "success": True,
            "data": {
                "viewer": {"id": "viewer-1"},
                "teams": {"nodes": []}
            }
        }

        with patch("builtins.print"):
            res = linear_api.cmd_create_manual_issues(
                api_key="fake-key",
                team_id=None,
                title="Single Issue Without Team"
            )

        self.assertFalse(res["success"])
        self.assertIn("Team ID could not be resolved", res["error"])
        self.assertEqual(res["issues"], [])

    @patch("linear_api.execute_graphql")
    @patch("linear_api.resolve_state_id")
    @patch("linear_api.resolve_or_create_label_id")
    def test_create_manual_issues_with_description_file(self, mock_resolve_label, mock_resolve_state, mock_execute):
        mock_resolve_state.return_value = "state-backlog-id"
        mock_resolve_label.return_value = "label-manual-id"
        mock_execute.return_value = {
            "success": True,
            "data": {
                "issueCreate": {
                    "success": True,
                    "issue": {
                        "id": "uuid-desc-file",
                        "identifier": "FAL-73",
                        "title": "Issue From File",
                        "url": "https://linear.app/fallkey/issue/FAL-73",
                        "state": {"name": "Backlog"},
                        "labels": {"nodes": [{"name": "manual"}]}
                    }
                }
            }
        }

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as f:
            f.write("## Contexto Arquivo\nDetalhes em Markdown")
            desc_file_path = f.name

        try:
            with patch("builtins.print"):
                res = linear_api.cmd_create_manual_issues(
                    api_key="fake-key",
                    team_id="team-1",
                    title="Issue From File",
                    description_file=desc_file_path
                )
            self.assertTrue(res["success"])
            self.assertEqual(res["issues"][0]["identifier"], "FAL-73")
            variables = mock_execute.call_args[0][2]
            self.assertIn("Contexto Arquivo", variables["input"]["description"])
        finally:
            if os.path.exists(desc_file_path):
                os.remove(desc_file_path)

    @patch("linear_api.resolve_api_key")
    @patch("linear_api.cmd_create_manual_issues")
    def test_cli_create_manual_issues_parses_arguments(self, mock_cmd_manual, mock_resolve_key):
        mock_resolve_key.return_value = "fake-api-key"
        test_args = [
            "linear_api.py",
            "create-manual-issues",
            "--title", "Test CLI Title",
            "--description", "Test CLI Desc",
            "--team-id", "team-123",
            "--project-id", "proj-456",
            "--priority", "2"
        ]
        with patch.object(sys, "argv", test_args):
            linear_api.main()

        mock_cmd_manual.assert_called_once_with(
            "fake-api-key",
            title="Test CLI Title",
            description="Test CLI Desc",
            description_file=None,
            batch_file=None,
            team_id="team-123",
            project_id="proj-456",
            priority=2
        )



if __name__ == "__main__":
    unittest.main()
