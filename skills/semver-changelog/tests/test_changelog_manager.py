#!/usr/bin/env python3
"""
Unit tests for changelog_manager.py
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to sys.path
import sys
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

import changelog_manager

class TestChangelogManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.changelog_path = Path(self.test_dir) / "CHANGELOG.md"

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_changelog(self):
        res = changelog_manager.init_changelog(self.changelog_path, initial_version="1.0.0")
        self.assertTrue(res["success"])
        self.assertTrue(res["created"])
        self.assertTrue(self.changelog_path.is_file())

        content = self.changelog_path.read_text(encoding="utf-8")
        self.assertIn("# Changelog", content)
        self.assertIn("## [Unreleased]", content)
        self.assertIn("## [1.0.0]", content)

        # Idempotent init
        res_repeat = changelog_manager.init_changelog(self.changelog_path)
        self.assertTrue(res_repeat["success"])
        self.assertFalse(res_repeat["created"])

    def test_add_entry_standard_category(self):
        changelog_manager.init_changelog(self.changelog_path)
        res = changelog_manager.add_entry(self.changelog_path, "Added", "New user login screen", issue="FAL-10")
        self.assertTrue(res["success"])
        self.assertFalse(res["already_existed"])

        content = self.changelog_path.read_text(encoding="utf-8")
        self.assertIn("### Added\n- New user login screen (FAL-10)", content)

    def test_add_entry_conventional_commit_aliases(self):
        changelog_manager.init_changelog(self.changelog_path)
        
        changelog_manager.add_entry(self.changelog_path, "feat", "Support biometric authentication")
        changelog_manager.add_entry(self.changelog_path, "fix", "Resolve crash on session expiration")
        changelog_manager.add_entry(self.changelog_path, "perf", "Optimize image decoding pipeline")
        changelog_manager.add_entry(self.changelog_path, "sec", "Upgrade crypto cipher suite")

        content = self.changelog_path.read_text(encoding="utf-8")
        self.assertIn("### Added\n- Support biometric authentication", content)
        self.assertIn("### Fixed\n- Resolve crash on session expiration", content)
        self.assertIn("### Changed\n- Optimize image decoding pipeline", content)
        self.assertIn("### Security\n- Upgrade crypto cipher suite", content)

    def test_add_entry_duplicate_handling(self):
        changelog_manager.init_changelog(self.changelog_path)
        res1 = changelog_manager.add_entry(self.changelog_path, "Added", "Duplicate item check")
        self.assertFalse(res1["already_existed"])

        res2 = changelog_manager.add_entry(self.changelog_path, "Added", "Duplicate item check")
        self.assertTrue(res2["already_existed"])

    def test_edit_entry(self):
        changelog_manager.init_changelog(self.changelog_path)
        changelog_manager.add_entry(self.changelog_path, "Added", "Initial wording of item")
        
        edit_res = changelog_manager.edit_entry(
            self.changelog_path,
            target="Initial wording",
            replacement="Refined and improved wording of item",
        )
        self.assertTrue(edit_res["success"])
        self.assertTrue(edit_res["modified"])

        content = self.changelog_path.read_text(encoding="utf-8")
        self.assertIn("- Refined and improved wording of item", content)
        self.assertNotIn("- Initial wording of item", content)

    def test_remove_entry(self):
        changelog_manager.init_changelog(self.changelog_path)
        changelog_manager.add_entry(self.changelog_path, "Fixed", "Temporary patch to remove")
        
        rem_res = changelog_manager.remove_entry(self.changelog_path, target="Temporary patch")
        self.assertTrue(rem_res["success"])
        self.assertTrue(rem_res["removed"])

        content = self.changelog_path.read_text(encoding="utf-8")
        self.assertNotIn("Temporary patch to remove", content)

    def test_calculate_next_version(self):
        # Patch bump
        v1 = changelog_manager.calculate_next_version("1.2.3", "patch", {})
        self.assertEqual(v1, "1.2.4")

        # Minor bump
        v2 = changelog_manager.calculate_next_version("1.2.3", "minor", {})
        self.assertEqual(v2, "1.3.0")

        # Major bump
        v3 = changelog_manager.calculate_next_version("1.2.3", "major", {})
        self.assertEqual(v3, "2.0.0")

        # Auto bump with Added -> minor
        v_auto_added = changelog_manager.calculate_next_version("1.0.0", "auto", {"Added": ["New feature"]})
        self.assertEqual(v_auto_added, "1.1.0")

        # Auto bump with only Fixed -> patch
        v_auto_fixed = changelog_manager.calculate_next_version("1.0.0", "auto", {"Fixed": ["Bug fix"]})
        self.assertEqual(v_auto_fixed, "1.0.1")

        # Auto bump with breaking change -> major (>=1.0.0)
        v_auto_breaking = changelog_manager.calculate_next_version(
            "1.2.0", "auto", {"Changed": ["BREAKING CHANGE: drop legacy API"]}
        )
        self.assertEqual(v_auto_breaking, "2.0.0")

    def test_bump_version_workflow(self):
        changelog_manager.init_changelog(self.changelog_path, initial_version="1.0.0")
        changelog_manager.add_entry(self.changelog_path, "feat", "Dark mode support")
        changelog_manager.add_entry(self.changelog_path, "fix", "Fix notification icon tint")

        bump_res = changelog_manager.bump_version(self.changelog_path, bump_type="auto", explicit_date="2026-10-21")
        self.assertTrue(bump_res["success"])
        self.assertEqual(bump_res["new_version"], "1.1.0")
        self.assertEqual(bump_res["release_date"], "2026-10-21")
        self.assertEqual(bump_res["items_released"], 2)

        content = self.changelog_path.read_text(encoding="utf-8")
        self.assertIn("## [1.1.0] - 2026-10-21", content)
        self.assertIn("### Added\n- Dark mode support", content)
        self.assertIn("### Fixed\n- Fix notification icon tint", content)
        self.assertIn("## [Unreleased]", content)

        # Status after bump should show 0 unreleased
        status = changelog_manager.get_status(self.changelog_path)
        self.assertEqual(status["total_unreleased_entries"], 0)
        self.assertEqual(status["current_version"], "1.1.0")

    def test_bump_version_empty_unreleased_raises(self):
        changelog_manager.init_changelog(self.changelog_path, initial_version="1.0.0")
        with self.assertRaises(ValueError):
            changelog_manager.bump_version(self.changelog_path, bump_type="patch")

    def test_detect_project_version(self):
        # Test pubspec.yaml detection
        pubspec = Path(self.test_dir) / "pubspec.yaml"
        pubspec.write_text("name: test_app\nversion: 2.4.1+12\n", encoding="utf-8")
        detected = changelog_manager.detect_project_version(Path(self.test_dir))
        self.assertEqual(detected, "2.4.1")

if __name__ == "__main__":
    unittest.main()
