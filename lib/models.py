from lib.utils import require_non_empty


class BaseEntity:
    """Shared id-registry and dict (de)serialization scaffolding for all model classes."""

    _registries = {}

    def __init__(self):
        registry = self.__class__._get_registry()
        self.id = len(registry) + 1
        registry.append(self)

    @classmethod
    def _get_registry(cls):
        return BaseEntity._registries.setdefault(cls, [])

    @classmethod
    def all(cls):
        return list(cls._get_registry())

    @classmethod
    def reset(cls):
        BaseEntity._registries[cls] = []

    def describe(self):
        raise NotImplementedError("Subclasses must implement describe().")


class User(BaseEntity):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.projects = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = require_non_empty(value, "User name")

    def add_project(self, project):
        project.owner = self
        if project not in self.projects:
            self.projects.append(project)

    def describe(self):
        return f"User #{self.id}: {self.name} ({len(self.projects)} project(s))"

    @classmethod
    def find_by_name(cls, name):
        return next((u for u in cls.all() if u.name.lower() == name.lower()), None)

    def to_dict(self):
        return {"id": self.id, "name": self.name}

    @classmethod
    def from_dict(cls, data):
        user = cls.__new__(cls)
        user.id = data["id"]
        user._name = data["name"]
        user.projects = []
        cls._get_registry().append(user)
        return user


class Project(BaseEntity):
    def __init__(self, name, owner):
        super().__init__()
        self.name = name
        self.owner = None
        self.tasks = []
        owner.add_project(self)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = require_non_empty(value, "Project name")

    def describe(self):
        owner_name = self.owner.name if self.owner else "unassigned"
        return f"Project #{self.id}: {self.name} (owner: {owner_name}, {len(self.tasks)} task(s))"

    @classmethod
    def find_by_name(cls, name):
        return next((p for p in cls.all() if p.name.lower() == name.lower()), None)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner.id if self.owner else None,
        }

    @classmethod
    def from_dict(cls, data, users_by_id):
        project = cls.__new__(cls)
        project.id = data["id"]
        project._name = data["name"]
        project.tasks = []
        owner = users_by_id.get(data["owner_id"])
        project.owner = owner
        if owner:
            owner.projects.append(project)
        cls._get_registry().append(project)
        return project


class Task(BaseEntity):
    def __init__(self, title, project):
        super().__init__()
        self.title = title
        self.project = project
        self.completed = False
        self.contributors = []
        project.tasks.append(self)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = require_non_empty(value, "Task title")

    def add_contributor(self, user):
        if user not in self.contributors:
            self.contributors.append(user)

    def complete(self):
        self.completed = True

    def describe(self):
        status = "complete" if self.completed else "open"
        return f"Task #{self.id}: {self.title} [{status}] in project '{self.project.name}'"

    @classmethod
    def find_by_id(cls, task_id):
        return next((t for t in cls.all() if t.id == task_id), None)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "project_id": self.project.id,
            "completed": self.completed,
            "contributor_ids": [u.id for u in self.contributors],
        }

    @classmethod
    def from_dict(cls, data, projects_by_id, users_by_id):
        task = cls.__new__(cls)
        task.id = data["id"]
        task._title = data["title"]
        task.completed = data["completed"]
        task.contributors = [
            users_by_id[uid] for uid in data.get("contributor_ids", []) if uid in users_by_id
        ]
        project = projects_by_id.get(data["project_id"])
        task.project = project
        if project:
            project.tasks.append(task)
        cls._get_registry().append(task)
        return task