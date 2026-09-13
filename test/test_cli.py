import subprocess
import sys
import os


def run_cli(tmp_path, *args):
    return subprocess.run(
        [sys.executable, os.path.join(os.getcwd(), "main.py"), *args],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )


def test_create_and_list_users(tmp_path):
    run_cli(tmp_path, "create-user", "Alice")
    result = run_cli(tmp_path, "list-users")
    assert "Alice" in result.stdout


def test_add_task_and_complete(tmp_path):
    run_cli(tmp_path, "create-user", "Alice")
    run_cli(tmp_path, "add-project", "Alice", "Website Redesign")
    run_cli(tmp_path, "add-task", "Website Redesign", "Design mockups")
    run_cli(tmp_path, "complete", "1")
    result = run_cli(tmp_path, "list-tasks", "Website Redesign")
    assert "done" in result.stdout.lower()