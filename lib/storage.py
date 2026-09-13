import json
import os

from lib.models import User, Project, Task

DEFAULT_PATH = os.path.join("data", "db.json")


def save_data(filepath=DEFAULT_PATH):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    data = {
        "users": [user.to_dict() for user in User.all()],
        "projects": [project.to_dict() for project in Project.all()],
        "tasks": [task.to_dict() for task in Task.all()],
    }

    try:
        with open(filepath, "w") as file:
            json.dump(data, file, indent=2)
    except OSError as error:
        raise RuntimeError(f"Could not save data to '{filepath}': {error}") from error


def load_data(filepath=DEFAULT_PATH):
    User.reset()
    Project.reset()
    Task.reset()

    if not os.path.exists(filepath):
        return

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"'{filepath}' is not valid JSON: {error}") from error
    except OSError as error:
        raise RuntimeError(f"Could not read data from '{filepath}': {error}") from error

    users_by_id = {u["id"]: User.from_dict(u) for u in data.get("users", [])}
    projects_by_id = {
        p["id"]: Project.from_dict(p, users_by_id) for p in data.get("projects", [])
    }
    for t in data.get("tasks", []):
        Task.from_dict(t, projects_by_id, users_by_id)