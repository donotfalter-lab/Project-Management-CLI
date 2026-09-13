import argparse

from rich.console import Console
from rich.table import Table
import pyfiglet

from lib.models import User, Project, Task
from lib.storage import load_data, save_data

console = Console()


def render_table(title, headers, rows):
    table = Table(title=title)
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*[str(value) for value in row])
    console.print(table)


def create_user(args):
    if User.find_by_name(args.name):
        console.print(f"[red]Error:[/red] a user named '{args.name}' already exists.")
        return
    user = User(args.name)
    console.print(f"[green]Created[/green] user '{user.name}' (id {user.id}).")


def list_users(args):
    users = User.all()
    if not users:
        console.print("No users yet. Use 'create-user <name>' to add one.")
        return
    rows = [[u.id, u.name, len(u.projects)] for u in users]
    render_table("Users", ["ID", "Name", "Projects"], rows)


def add_project(args):
    user = User.find_by_name(args.user)
    if not user:
        console.print(f"[red]Error:[/red] no user named '{args.user}'.")
        return
    project = Project(args.name, user)
    console.print(f"[green]Added[/green] project '{project.name}' (id {project.id}) to {user.name}.")


def list_projects(args):
    user = User.find_by_name(args.user)
    if not user:
        console.print(f"[red]Error:[/red] no user named '{args.user}'.")
        return
    if not user.projects:
        console.print(f"{user.name} has no projects yet.")
        return
    rows = [[p.id, p.name, len(p.tasks)] for p in user.projects]
    render_table(f"Projects for {user.name}", ["ID", "Project", "Tasks"], rows)


def add_task(args):
    project = Project.find_by_name(args.project)
    if not project:
        console.print(f"[red]Error:[/red] no project named '{args.project}'.")
        return
    task = Task(args.title, project)
    console.print(f"[green]Added[/green] task '{task.title}' (id {task.id}) to project '{project.name}'.")


def list_tasks(args):
    project = Project.find_by_name(args.project)
    if not project:
        console.print(f"[red]Error:[/red] no project named '{args.project}'.")
        return
    if not project.tasks:
        console.print(f"Project '{project.name}' has no tasks yet.")
        return
    rows = [
        [t.id, t.title, "done" if t.completed else "open",
         ", ".join(u.name for u in t.contributors) or "none"]
        for t in project.tasks
    ]
    render_table(f"Tasks for {project.name}", ["ID", "Title", "Status", "Contributors"], rows)


def assign_contributor(args):
    task = Task.find_by_id(args.task_id)
    if not task:
        console.print(f"[red]Error:[/red] no task with id {args.task_id}.")
        return
    user = User.find_by_name(args.user)
    if not user:
        console.print(f"[red]Error:[/red] no user named '{args.user}'.")
        return
    task.add_contributor(user)
    console.print(f"[green]Added[/green] {user.name} as a contributor on task '{task.title}'.")


def complete_task(args):
    task = Task.find_by_id(args.task_id)
    if not task:
        console.print(f"[red]Error:[/red] no task with id {args.task_id}.")
        return
    task.complete()
    console.print(f"[green]Task '{task.title}' marked as complete.[/green]")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pm",
        description="Manage users, projects, and tasks from the command line.",
    )
    subparsers = parser.add_subparsers(title="commands", dest="command")

    p = subparsers.add_parser("create-user", help="Create a new user.")
    p.add_argument("name", help="The user's display name.")
    p.set_defaults(func=create_user)

    p = subparsers.add_parser("list-users", help="List all users.")
    p.set_defaults(func=list_users)

    p = subparsers.add_parser("add-project", help="Add a project owned by a user.")
    p.add_argument("user", help="The owning user's name.")
    p.add_argument("name", help="The new project's name.")
    p.set_defaults(func=add_project)

    p = subparsers.add_parser("list-projects", help="List a user's projects.")
    p.add_argument("user", help="The user's name.")
    p.set_defaults(func=list_projects)

    p = subparsers.add_parser("add-task", help="Add a task to a project.")
    p.add_argument("project", help="The project's name.")
    p.add_argument("title", help="The new task's title.")
    p.set_defaults(func=add_task)

    p = subparsers.add_parser("list-tasks", help="List a project's tasks.")
    p.add_argument("project", help="The project's name.")
    p.set_defaults(func=list_tasks)

    p = subparsers.add_parser("assign", help="Add a contributor to a task.")
    p.add_argument("task_id", type=int, help="The task's id.")
    p.add_argument("user", help="The contributing user's name.")
    p.set_defaults(func=assign_contributor)

    p = subparsers.add_parser("complete", help="Mark a task as complete.")
    p.add_argument("task_id", type=int, help="The task's id.")
    p.set_defaults(func=complete_task)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not getattr(args, "command", None):
        console.print(pyfiglet.figlet_format("PM CLI", font="slant"))
        parser.print_help()
        return

    load_data()

    try:
        args.func(args)
    except ValueError as error:
        console.print(f"[red]Input Error:[/red] {error}")
        return
    except RuntimeError as error:
        console.print(f"[red]Service Error:[/red] {error}")
        return

    save_data()


if __name__ == "__main__":
    main()