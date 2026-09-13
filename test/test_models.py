import pytest

from lib.models import User, Project, Task


@pytest.fixture(autouse=True)
def reset_registries():
    User.reset()
    Project.reset()
    Task.reset()
    yield


def test_user_creation_and_validation():
    user = User("Alice")
    assert user.name == "Alice"

    with pytest.raises(ValueError):
        User("   ")


def test_project_belongs_to_one_user():
    user = User("Alice")
    project = Project("Website Redesign", user)

    assert project.owner is user
    assert project in user.projects


def test_task_supports_many_to_many_contributors():
    user1 = User("Alice")
    user2 = User("Bob")
    project = Project("Website Redesign", user1)
    task = Task("Design mockups", project)

    task.add_contributor(user1)
    task.add_contributor(user2)

    assert user1 in task.contributors
    assert user2 in task.contributors


def test_task_complete_updates_status():
    user = User("Alice")
    project = Project("Website Redesign", user)
    task = Task("Design mockups", project)

    task.complete()

    assert task.completed is True


def test_describe_is_polymorphic():
    user = User("Alice")
    project = Project("Website Redesign", user)
    task = Task("Design mockups", project)

    assert "User" in user.describe()
    assert "Project" in project.describe()
    assert "Task" in task.describe()