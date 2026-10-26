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

if __name__ == "__main__":
    unittest.main()
