import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "workflow" / "bundle_context.py"
SPEC = importlib.util.spec_from_file_location("bundle_context", MODULE_PATH)
bundle_context = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(bundle_context)


class BundleContextTests(unittest.TestCase):
    def test_builds_markdown_and_manifest_with_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "workflow").mkdir()
            (root / "Reference_info").mkdir()
            (root / "Reference_info" / "profile.md").write_text(
                "# Profile\n\nPython and Bash experience.\n", encoding="utf-8"
            )
            (root / "Job_descriptions").mkdir()
            (root / "Job_descriptions" / "job.md").write_text(
                "Build data pipelines.", encoding="utf-8"
            )
            (root / "workflow" / "source_registry.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "groups": [
                            {
                                "name": "personal",
                                "trust": "primary-fact",
                                "include": ["Reference_info/*.md"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            bundle_dir = bundle_context.build_bundle(
                root,
                Path("Job_descriptions/job.md"),
                root / "workflow/source_registry.json",
                root / ".workflow/bundles",
            )

            manifest = json.loads(
                (bundle_dir / "manifest.json").read_text(encoding="utf-8")
            )
            context = (bundle_dir / "context.md").read_text(encoding="utf-8")
            self.assertEqual(manifest["job_description"], "Job_descriptions/job.md")
            self.assertEqual(manifest["sources"][1]["path"], "Reference_info/profile.md")
            self.assertIn("Build data pipelines.", context)
            self.assertIn("Python and Bash experience.", context)

    def test_requests_copilot_summary_for_long_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "workflow").mkdir()
            (root / "Reference_info").mkdir()
            (root / "Reference_info" / "journal.md").write_text(
                "A factual achievement. " * 20, encoding="utf-8"
            )
            (root / "job.md").write_text("A job.", encoding="utf-8")
            registry = {
                "version": 1,
                "groups": [
                    {
                        "name": "facts",
                        "trust": "primary-fact",
                        "include": ["Reference_info/*.md"],
                    }
                ],
            }
            registry_path = root / "workflow/source_registry.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            bundle_dir = bundle_context.build_bundle(
                root,
                Path("job.md"),
                registry_path,
                root / ".workflow/bundles",
                summary_threshold=20,
            )

            manifest = json.loads(
                (bundle_dir / "manifest.json").read_text(encoding="utf-8")
            )
            request = manifest["summarization"]["requests"][0]
            self.assertEqual(request["source"], "Reference_info/journal.md")
            self.assertEqual(manifest["summarization"]["provider"], "copilot-agent")

    def test_rejects_empty_approved_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "workflow").mkdir()
            (root / "Reference_info").mkdir()
            (root / "Reference_info" / "empty.md").write_text("", encoding="utf-8")
            (root / "job.md").write_text("A job.", encoding="utf-8")
            registry_path = root / "workflow/source_registry.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "groups": [
                            {
                                "name": "facts",
                                "trust": "primary-fact",
                                "include": ["Reference_info/*.md"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(bundle_context.BundleError):
                bundle_context.build_bundle(
                    root, Path("job.md"), registry_path, root / ".workflow/bundles"
                )

    def test_does_not_overwrite_existing_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "workflow").mkdir()
            (root / "Reference_info").mkdir()
            (root / "Reference_info" / "profile.md").write_text(
                "A fact.", encoding="utf-8"
            )
            (root / "job.md").write_text("A job.", encoding="utf-8")
            registry_path = root / "workflow/source_registry.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "groups": [
                            {
                                "name": "facts",
                                "trust": "primary-fact",
                                "include": ["Reference_info/*.md"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_root = root / ".workflow/bundles"

            first = bundle_context.build_bundle(
                root, Path("job.md"), registry_path, output_root
            )
            second = bundle_context.build_bundle(
                root, Path("job.md"), registry_path, output_root
            )

            self.assertEqual(first.name, "job")
            self.assertEqual(second.name, "job-2")


if __name__ == "__main__":
    unittest.main()
