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
            title="feat(linear-workflow): new title"
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
        fk_new_issue = (skill_root / ".apm" / "skills" / "fk-new-issue" / "SKILL.md").read_text(encoding="utf-8")
        fk_tech_analysis = (skill_root / ".apm" / "skills" / "fk-technical-analysis" / "SKILL.md").read_text(encoding="utf-8")
        main_skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")

        for content in (fk_new_issue, fk_tech_analysis, main_skill):
            self.assertIn("Proibição de Consent Gate Cego", content)
            self.assertIn("Resumo", content)

        self.assertIn("Feature", fk_new_issue)
        self.assertIn("não force `Back`", fk_new_issue)
        self.assertIn("Feature", main_skill)
        self.assertIn("não force `Back`", main_skill)

    def test_skill_files_enforce_mandatory_title_and_description_in_tech_analysis(self):
        skill_root = Path(__file__).resolve().parent.parent
        fk_tech_skill = (skill_root / ".apm" / "skills" / "fk-technical-analysis" / "SKILL.md").read_text(encoding="utf-8")
        fk_tech_prompt = (skill_root / ".apm" / "prompts" / "fk-technical-analysis.prompt.md").read_text(encoding="utf-8")
        instructions = (skill_root / ".apm" / "instructions" / "linear-lifecycle-commands.instructions.md").read_text(encoding="utf-8")
        main_skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        multi_harness = (skill_root / "references" / "multi-harness-commands.md").read_text(encoding="utf-8")
        states_ref = (skill_root / "references" / "states-and-labels.md").read_text(encoding="utf-8")

        for content in (fk_tech_skill, fk_tech_prompt, instructions, main_skill):
            self.assertIn("Título Revisado", content)
            self.assertIn("Descrição Atualizada", content)
            self.assertIn("--title", content)
            self.assertIn("--description", content)

        self.assertNotIn("Atualização de Descrição (Opcional / Recomendado)", fk_tech_skill)
        self.assertNotIn("opcionalmente na descrição do card", fk_tech_prompt)
        self.assertNotIn("opcionalmente na descrição do card", instructions)
        self.assertNotIn("Opcionalmente, caso o escopo técnico tenha sido significativamente refinado", main_skill)
        self.assertNotIn("optionally updating the card description", multi_harness)
        self.assertIn("mandatorily updating the card title (`--title`) and description", multi_harness)
        self.assertIn("--title", states_ref)
        self.assertIn("--description", states_ref)

if __name__ == "__main__":
    unittest.main()
