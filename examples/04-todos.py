"examples/04-todos.py"

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pulse as ps

TodosFilter = Literal["all", "active", "completed"]


@ps.reactive
@dataclass
class Todo:
    id: int
    title: str
    completed: bool


class TodosState(ps.State):
    todos: list[Todo]
    new_title: str = ""
    filter: TodosFilter = "all"

    def __init__(self):
        self.todos = [
            Todo(id=1, title="Ship Pulse demo", completed=False),
            Todo(id=2, title="Write docs", completed=True),
        ]
        print("Todos is a reactive list:", isinstance(self.todos, ps.ReactiveList))

    @ps.computed
    def filtered(self) -> list[Todo]:
        if self.filter == "active":
            return [t for t in self.todos if not t.completed]
        if self.filter == "completed":
            return [t for t in self.todos if t.completed]
        return self.todos

    def add(self):
        title = self.new_title.strip()
        if not title:
            return
        next_id = max([t.id for t in self.todos], default=0) + 1
        self.todos.append(Todo(id=next_id, title=title, completed=False))
        self.new_title = ""

    def remove(self, todo_id: int):
        self.todos = [t for t in self.todos if t.id != todo_id]

    def toggle(self, todo_id: int):
        for t in self.todos:
            if t.id == todo_id:
                t.completed = not t.completed

    def set_filter(self, value: TodosFilter):
        self.filter = value


def TodoItem(state: TodosState, todo: Todo):
    return ps.div(
        ps.input(
            type="checkbox",
            checked=todo.completed,
            onChange=lambda: state.toggle(todo.id),
            className="mr-2",
        ),
        ps.span(
            todo.title,
            className=("line-through text-gray-500" if todo.completed else ""),
        ),
        ps.button(
            "✕",
            onClick=lambda: state.remove(todo.id),
            className="ml-3 text-red-600",
        ),
        key=str(todo.id),
        className="flex items-center mb-2",
    )


@ps.component
def TodosPage():
    state = ps.states(TodosState)

    return ps.div(
        className="max-w-xl mx-auto h-screen flex flex-col justify-center items-start"
    )[
        ps.h2("Todos", className="text-xl font-bold mb-3"),
        # Add
        ps.div(
            ps.input(
                type="text",
                placeholder="Add a todo...",
                value=state.new_title,
                onChange=lambda e: setattr(state, "new_title", e["target"]["value"]),
                className="border p-2 mr-2",
            ),
            ps.button(
                "Add",
                onClick=state.add,
                disabled=not state.new_title.strip(),
                className="btn-primary",
            ),
            className="mb-4",
        ),
        # Filter
        ps.div(
            ps.button(
                "All",
                onClick=lambda: state.set_filter("all"),
                className="mr-2 "
                + ("bg-blue-600 text-white px-2" if state.filter == "all" else "px-2"),
            ),
            ps.button(
                "Active",
                onClick=lambda: state.set_filter("active"),
                className="mr-2 "
                + (
                    "bg-blue-600 text-white px-2"
                    if state.filter == "active"
                    else "px-2"
                ),
            ),
            ps.button(
                "Completed",
                onClick=lambda: state.set_filter("completed"),
                className=(
                    "bg-blue-600 text-white px-2"
                    if state.filter == "completed"
                    else "px-2"
                ),
            ),
            className="mb-4",
        ),
        # List
        ps.div(
            [TodoItem(state, t) for t in state.filtered]
            if state.filtered
            else ps.p("No todos", className="italic text-gray-500"),
        ),
    ]


app = ps.App(
    routes=[ps.Route("/", TodosPage)],
    codegen=ps.CodegenConfig(web_dir=Path(__file__).parent.parent / "pulse-web"),
)
