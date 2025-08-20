"examples/04-todos.py"

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pulse as ps

TodosFilter = Literal["all", "active", "completed"]


# Makes the dataclass reactive, so that Pulse can detect when its properties are
# mutated.
@ps.reactive
@dataclass
class Todo:
    id: int
    title: str
    completed: bool


class TodosState(ps.State):
    todos: list[Todo]
    filter: TodosFilter = "all"

    def __init__(self):
        # self.todos gets converted into a ReactiveList automatically
        self.todos = [
            Todo(id=1, title="Ship Pulse demo", completed=False),
            Todo(id=2, title="Write docs", completed=True),
        ]

    @ps.computed
    def filtered(self) -> list[Todo]:
        if self.filter == "active":
            return [t for t in self.todos if not t.completed]
        if self.filter == "completed":
            return [t for t in self.todos if t.completed]
        return self.todos

    def add_todo(self, title: str):
        next_id = max([t.id for t in self.todos], default=0) + 1
        # self.todos is a ReactiveList, so Pulse detects .append() and updates the applicaiton
        self.todos.append(Todo(id=next_id, title=title, completed=False))

    def remove(self, todo_id: int):
        self.todos = [t for t in self.todos if t.id != todo_id]

    def toggle(self, todo_id: int):
        for t in self.todos:
            if t.id == todo_id:
                t.completed = not t.completed

    def set_filter(self, value: TodosFilter):
        self.filter = value


class AddTodoState(ps.State):
    new_title: str = ""

    def __init__(self, todo_state: TodosState):
        self._todo_state = todo_state

    def on_change(self, value: str):
        self.new_title = value

    @ps.computed
    def disabled(self) -> bool:
        return len(self.new_title.strip()) < 3

    def on_add(self):
        if not self.disabled:
            self._todo_state.add_todo(self.new_title)


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
    def setup_fn():
        todos = TodosState()
        add_todo = AddTodoState(todos)
        return todos, add_todo

    todos, add_todo = ps.setup(setup_fn)

    return ps.div(
        className="max-w-xl mx-auto h-screen flex flex-col justify-center items-start"
    )[
        ps.h2("Todos", className="text-xl font-bold mb-3"),
        # Add
        ps.div(
            ps.input(
                type="text",
                placeholder="Add a todo...",
                value=add_todo.new_title,
                onChange=lambda evt: add_todo.on_change(evt["target"]["value"]),
                className="border p-2 mr-2",
            ),
            ps.button(
                "Add",
                onClick=add_todo.on_add,
                disabled=add_todo.disabled,
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            className="mb-4",
        ),
        # Filter
        ps.div(
            ps.button(
                "All",
                onClick=lambda: todos.set_filter("all"),
                className="mr-2 "
                + ("bg-blue-600 text-white px-2" if todos.filter == "all" else "px-2"),
            ),
            ps.button(
                "Active",
                onClick=lambda: todos.set_filter("active"),
                className="mr-2 "
                + (
                    "bg-blue-600 text-white px-2"
                    if todos.filter == "active"
                    else "px-2"
                ),
            ),
            ps.button(
                "Completed",
                onClick=lambda: todos.set_filter("completed"),
                className=(
                    "bg-blue-600 text-white px-2"
                    if todos.filter == "completed"
                    else "px-2"
                ),
            ),
            className="mb-4",
        ),
        # Todos
        ps.div(
            [TodoItem(todos, t) for t in todos.filtered]
            if todos.filtered
            else ps.p("No todos", className="italic text-gray-500"),
        ),
    ]


app = ps.App(
    routes=[ps.Route("/", TodosPage)],
    codegen=ps.CodegenConfig(web_dir=Path(__file__).parent.parent / "pulse-web"),
)
