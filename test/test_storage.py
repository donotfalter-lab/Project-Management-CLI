import pytest

from lib.models import User, Project, Task
from lib.storage import save_data, load_data


@pytest.fixture(autouse=True)
def reset_registries():
    User.reset()
    Project.reset()
    Task.reset()
    yield


def test_save_and_load_round_trip(tmp_path):
    filepath = tmp_path / "db.json"

    user = User("Alice")
    project = Project("Website Redesign", user)
    task = Task("Design mockups", project)
    task.add_contributor(user)
    task.complete()

    save_data(str(filepath))

    User.reset()
    Project.reset()
    Task.reset()

    load_data(str(filepath))

    loaded_user = User.find_by_name("Alice")
    loaded_project = Project.find_by_name("Website Redesign")

    assert loaded_project.owner is loaded_user
    assert loaded_project.tasks[0].completed is True
    assert loaded_user in loaded_project.tasks[0].contributors


def test_load_data_missing_file_starts_empty(tmp_path):
    load_data(str(tmp_path / "does_not_exist.json"))
    assert User.all() == []


def test_load_data_raises_runtime_error_on_invalid_json(tmp_path):
    filepath = tmp_path / "bad.json"
    filepath.write_text("not valid json")

    with pytest.raises(RuntimeError):
        load_data(str(filepath))