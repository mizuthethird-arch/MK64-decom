import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = SOURCE_ROOT / ".github" / "workflows" / "ci.yml"

GATE = "vars.MK64_PLAN_CHECK == 'on'"
EXPECTED_GATE_COUNT = 2


def workflow_text():
    return WORKFLOW.read_text(encoding="utf-8")


def job_blocks(text):
    """Splits the jobs section into per-job text, keyed by the job's display name."""
    blocks = {}
    current_name = None
    current_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("name:") and line.startswith("    name:"):
            if current_name is not None:
                blocks[current_name] = "\n".join(current_lines)
            current_name = stripped.split(":", 1)[1].strip().strip("\"'")
            current_lines = [line]
            continue
        if current_name is not None:
            current_lines.append(line)
    if current_name is not None:
        blocks[current_name] = "\n".join(current_lines)
    return blocks


class PlanJobsGuardTest(unittest.TestCase):
    """The two gated plan jobs must exist and stay gated, or nothing notices their removal."""

    def setUp(self):
        self.assertTrue(WORKFLOW.is_file(), f"{WORKFLOW} must exist")
        self.text = workflow_text()
        self.jobs = job_blocks(self.text)

    def test_the_plan_lint_job_exists_and_runs_its_runner(self):
        self.assertIn("plan lint", self.jobs)
        self.assertIn("tools/ci/plan_lint_run.py", self.jobs["plan lint"])

    def test_the_screen_coverage_job_exists_and_runs_its_runner(self):
        self.assertIn("screen coverage", self.jobs)
        self.assertIn("tools/ci/coverage_lint_run.py", self.jobs["screen coverage"])

    def test_both_jobs_are_gated_by_the_same_variable(self):
        self.assertEqual(self.text.count(GATE), EXPECTED_GATE_COUNT)

    def test_the_plan_lint_job_is_gated(self):
        self.assertIn(GATE, self.jobs["plan lint"])

    def test_the_screen_coverage_job_is_gated(self):
        self.assertIn(GATE, self.jobs["screen coverage"])

    def test_neither_gated_job_runs_unconditionally(self):
        for name in ("plan lint", "screen coverage"):
            with self.subTest(job=name):
                self.assertIn("if:", self.jobs[name])


if __name__ == "__main__":
    unittest.main(verbosity=2)
