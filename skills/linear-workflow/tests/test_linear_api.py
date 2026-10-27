import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import sys
import os

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

if __name__ == "__main__":
    unittest.main()
