# The Pulse tutorial

Welcome to the Pulse tutorial! In this guide, we'll work through examples that cover all the key concepts of the Pulse framework.

## Setup

- [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/)
- [Install Bun](https://bun.com/docs/installation)
- Run `uv sync` to install Python dependencies
- Run `cd pulse-web && bun i` to install JavaScript dependencies
- Activate the Python virtual environment:
  - Linux/macOS: `source .venv/bin/activate`
  - Windows: `.venv\Scripts\Activate`

You're good to go! Now execute `pulse run tutorial.py`. Your terminal should display two pane, with the Python server on the left and the React app on the right. Use `q` to stop the app.

Go to the address given by the React app on the right, most likely http://localhost:5173, to see the final app.

The Pulse server and React app automatically reload the app if you make changes during development.

> [!NOTE]
> This tutorial will use [Tailwind CSS](https://tailwindcss.com/) for styling. If you are not familiar with it, you can just ignore the CSS classes passed as `className`.

## 1. Defining the App

A Pulse application is defined by creating an `App` object, which defines the routes and other code generation options.

```python
"Full example: steps/01-basic-app.py"

from pathlib import Path
import pulse as ps


@ps.component
def welcome():
    return ps.div(
        className="min-h-screen flex items-center justify-center flex-col bg-gray-100"
    )[
        ps.h1("Welcome to Pulse!", className="text-4xl font-bold text-blue-600 mb-4"),
        ps.p(
            "You've created your first Pulse application!",
            className="text-lg text-gray-700",
        ),
    ]


app = ps.App(
    routes=[ps.Route("/", welcome)],
    codegen=ps.CodegenConfig(web_dir=Path(__file__).parent.parent / "pulse-web"),
)
```

Each route defines its path and its component, which is a function that takes no argument and returns Pulse elements (HTML tags in this case). It is wrapped by `@ps.component`, we will see what this decorator does later in the tutorial.

Like all steps of this tutorial, you will find it in the `steps/` folder in this repository. Run it using:

```
pulse run steps/01-basic-app.py
```

## 2. HTML and Pulse syntax

The main objective of Pulse is to display something on a web page. As such, the most basic building blocks are HTML elements. They are built into Pulse, so you can simply use `ps.div()` or `ps.a`.

The code seen earlier:

```python
ps.div(
    className="min-h-screen flex items-center justify-center flex-col bg-gray-100"
)[
    ps.h1("Welcome to Pulse!", className="text-4xl font-bold text-blue-600 mb-4"),
    ps.p(
        "You've created your first Pulse application!",
        className="text-lg text-gray-700",
    ),
]
```

Translates to this HTML:

```html
<div class="min-h-screen flex items-center justify-center flex-col bg-gray-100">
  <h1 class="text-4xl font-bold text-blue-600 mb-4">Welcome to Pulse!</h1>
  <p class="text-lg text-gray-700">
    You've created your first Pulse application!
  </p>
</div>
```

All Pulse elements, including HTML ones, can receive _props_ (in React terms), or _attributes_ (in HTML terms), and child elements, if they accept them. Props are passed as keyword arguments like `className` in the example above, children are passed as positional arguments.

> [!NOTE]
> Pulse adopts React conventions, which means that the HTML attribute `class` is renamed to `className`, to avoid conflicts with the `class` keyword in JavaScript or Python.

You may have noticed that our earlier example showcases two ways of passing children to a Pulse element:

1. As positional arguments when calling the function, like `ps.div("content")`
2. By using indexing syntax after defining the props, like `ps.div(className="...")["content]"`

Option 1. is convenient when the element doesn't have many children. Option 2. resembles HTML more and keeps the attributes close to the element's definition.

```python
ps.div(
    # Having the className stay close to the `ps.div` and passing in the children afterwards is more readable for this div.
    className="min-h-screen flex items-center justify-center flex-col bg-gray-100"
)[
    # Passing in the content as first argument is easier for this h1.
    ps.h1("Welcome to Pulse!", className="text-4xl font-bold text-blue-600 mb-4"),
    ps.p(
        "You've created your first Pulse application!",
        className="text-lg text-gray-700",
    ),
]
```

## 3. State

The most important concept in order to build an interactive application is how to define its state and how it can be modified by users.

The easiest way to demonstrate how it works in Pulse is with a counter:

```python
"Full example: steps/02-counter.py"
import pulse as ps

class CounterState(ps.State):
    count: int = 0

    def increment(self):
        self.count += 1


@ps.component
def counter():
    state = ps.states(CounterState)
    print(f"Rendering counter, count is {state.count}")

    def decrement():
        state.count -= 1

    return ps.div(
        # Display current count
        ps.p(f"Current count: {state.count}", className="text-lg"),
        # Control buttons
        ps.div(className="flex items-center space-x-2")[
            ps.button(
                "Decrement (-1)",
                onClick=decrement,
                className="bg-red-500 text-white px-4 py-2 rounded mr-4 hover:bg-red-600",
            ),
            ps.button(
                "Increment (+1)",
                onClick=state.increment,
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600",
            ),
        ],
    )
```

You can run the full example using `pulse run steps/02-counter.py`.

Here we see:

- A state is defined as a class that inherits from `pulse.State`.
- State properties are defined as `count: int = 0` with a type annotation and eventual default value.
- Users modify state through events, like `onClick`.
- Event handlers can be a state method or any other function.
- When state is modified, the application reruns (we call this _"rerendering"_) and the user interface is updated.
- You should see the `print` statement in your terminal after every click on increment or decrement.

So the core loop of Pulse is:

1. Define the state.
2. Render the application based on the state.
3. User interacts with the application, modifies the state.
4. Application rerenders, returning the updated user interface.
5. Pulse performs a _diff_ between the current and updated UIs and only sends update operations to the user's browser.

## 4. Hooks

### 4.1. Introduction: `ps.states`

You may have noticed that our earlier state example uses a function called `ps.states`. This function is a **Pulse hook**, providing a special mechanism outside the usual render -> update -> render cycle.

Its purpose is to preserve the same state instance across component rerenders. To see why this matters, try making this change in `02-counter.py`:

```diff
@ps.component
def counter():
-    state = ps.states(CounterState)
+    state = CounterState()
```

You should notice that clicking the buttons doesn't do anything anymore. Here is what happens:

- 1st render: `CounterState` is created.
- Click increment: `count` in `CounterState` is incremented.
- 2nd render: a new `CounterState` is created. The count is at its default value of 0. The rest of the component uses this state and displays that count is 0.

With `ps.states`, this becomes:

- 1st render: `CounterState` is created.
- Click increment: `count` in `CounterState` is incremented.
- 2nd render: `ps.states` returns the same state as on the 1st render. The count has been incremented and is now 1. The rest of the component uses this state and thus displays that count is 1.

### 4.2. Rules of hooks

The three main Pulse hooks are:

- `ps.setup`: runs an arbitrary function on first render and returns its result on every render aftewards.
- `ps.states`: preserves states across rerenders.
- `ps.effects`: sets up effects on first render.

They have one single rule: **you can only call them once per component.**

Components are functions decorated with `@ps.component`. We will discuss them in the [Components](#7-components) section.

This rule illustrates that the purpose of hooks is to **give you a way to do something exactly once, when a component first renders**.

In practice, you could do everything with `ps.setup`: create your states, set up your effects, initialize something, etc... `ps.states` and `ps.effects` are convenience hooks for common requirements.

### 4.3. Usage

Let's understand how to use hooks by looking at an example. I will not use `ps.effects` here, as it will be introduced in [Effects](#9-effects).

The code is available in [`examples/03-hooks.py`](./examples/03-hooks.py)

```python
"examples/03-hooks.py"

from pathlib import Path
import pulse as ps


class CounterState(ps.State):
    count: int = 0

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1


class DebugState(ps.State):
    enabled: bool = True

    def __init__(self, enabled: bool):
        self.enabled = enabled

    def toggle(self):
        self.enabled = not self.enabled


def setup_demo(arg, *, kwarg):
    print(f"Received argument: {arg} and kwarg: {kwarg}")
    # do anything else here
    return DebugState(True)


def render_counter(label: str, state: CounterState):
    return ps.div(className="flex items-center gap-2")[
        ps.button(
            "-",
            onClick=state.decrement,
            className="px-2 py-1 bg-red-500 text-white rounded",
        ),
        ps.span(f"{label}: {state.count}"),
        ps.button(
            "+",
            onClick=state.increment,
            className="px-2 py-1 bg-green-500 text-white rounded",
        ),
    ]


def debug_toggle(label: str, state: DebugState):
    return ps.label(className="flex items-center gap-2")[
        ps.input(type="checkbox", checked=state.enabled, onChange=state.toggle),
        f"{label}: {state.enabled}",
    ]


@ps.component
def HooksDemo():
    # Three ways of creating states with `ps.states`:
    # - Pass an instance: `Counter()`
    # - Pass a function returning a state.
    # If a state doesn't have a constructor, or it takes no arguments, passing in
    # the state class is like passing in a function.
    counter1, counter2, debug1 = ps.states(
        CounterState, CounterState(), lambda: DebugState(False)
    )

    # `ps.setup` can also be used to create states and perform anything else you
    # need to set up on the first render. Note that the setup function has to be
    # synchronous, it is not recommended to perform async operations, like
    # network requests, there.
    debug2 = ps.setup(setup_demo, "arg", kwarg="kwarg")

    return ps.div(
        className="w-xl mx-auto h-screen flex flex-col justify-center items-start"
    )[
        ps.h3("Setup + States demo", className="text-2xl font-bold mb-4"),
        ps.div(className="space-y-4")[
            render_counter("Counter 1", counter1),
            render_counter("Counter 2", counter2),
            ps.div(className="flex flex-col gap-2")[
                debug_toggle("Debug 1", debug1), debug_toggle("Debug 2", debug2)
            ],
        ],
    ]


app = ps.App(
    routes=[ps.Route("/", HooksDemo)],
    codegen=ps.CodegenConfig(web_dir=Path(__file__).parent.parent / "pulse-web"),
)
```

In this example, we can see:

- Using `ps.states` with a function producing a state. The function is executed on first render and its result stored for all subsequent calls. For example:
  - Example 1: `ps.states(CounterState)`. The constructor takes no arguments, so it works.
  - Example 2: `ps.states(lambda: DebugState(True))`. This is an easy way to wrap a constructor that takes arguments.
- Using `ps.states` with a component instance: `CounterState()`. On first render, the state is stored and returned. On subsequent renders, a new `CounterState` is created in our function and disposed immediately within `ps.states`, which returns the stored state
  - Example: `ps.states(CounterState())`
  - This pattern works fine and is often convenient.
  - Keep in mind that a new `CounterState` is constructed on every render, so if the state constructor does resource-intensive work, you should probably wrap it in a function, like above.
- Using `ps.setup` with a function that takes in arguments. The function will be called once, its result stored and returned on every render. Arguments to the function can be passed to `ps.setup()` after the function.
  - Here, we use it to create a `DebugState`, essentially doing the same thing as `ps.states`
  - This is useful if you have more complex initialization needs. See the [Cookbook](#15-cookbook) for usage examples.

## 5. State (part II)

Now that we understand how hooks work, everything in the first state demo ([`examples/02-counter.py`](./examples/02-counter.py)) should be clear. States are one of Pulse's central features and they have more features we haven't discussed yet, so let's explore them.

We're going to use a TODO list example to guide us through this section and the next. You can find the code in [`examples/04-todos.py`](./examples/04-todos.py)

```python
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

```

Let's break it down piece by piece.

### 5.1. Deep reactivity

In our example, you can see that `TodosState` stores a list of Todo objects. In order to update it, we could rebuild it and update the property. For example:

```python
def add_todo(self, todo: Todo):
    self.todos = [*self.todos, todo]
```

This works the same way as the counter updates we saw earlier.

However, Pulse supports **deep reactivity**:

- _Reactivity_ means that when a state change happens, Pulse can propagate updates where they are needed.
- _Deep_ means that Pulse is able to detect changes that are deeper than the property defined on the state

This means `TodosState` can just use `self.todos.append()` when adding a todo, or directly update a property on a todo like `todo.completed = not todo.completed`, and Pulse will still detect the change and rerender the application accordingly.

```python
# Simplifying the code, we get this:
class TodosState(ps.State):
    todos: list[Todo]

    def __init__(self):
        self.todos = [...]
        print(isinstance(self.todos, ps.ReactiveList)) # should print True

    def add(self):
        self.todos.append(Todo(id=next_id, title=title, completed=False))

    def toggle_todo(self, todo_id: int):
        for t in self.todos:
            if t.id == todo_id:
                t.completed = not t.completed
```

This works because Pulse has special versions of lists, sets, and dictionaries that are applied automatically to any value stored in a state. In the constructor, you can see that `self.todos` gets converted into `ps.ReactiveList`. It behaves exactly like a regular list, except `self.todos.append()` is detected by Pulse's update system.

The same thing applies for dictionaries and sets. The transformation is also applied recursively, so all nested lists, sets, and dictionaries get converted as well.

For the `Todo` class itself, you may have noticed it is decorated with `@ps.reactive`. This function converts the class into a reactive dataclass, allowing Pulse to detect changes like `t.completed = not t.completed`. Currently, this has to be done manually on the class definition, but I'm working on automating this conversion.

In general, it is recommended that any custom data structure within a state property uses a dataclass tagged with `@ps.reactive`.

Overall, this system exists to make Pulse work like regular Python, except all changes are detected and used to update the application.

### 5.2. Computeds

Another new feature introduced here is the usage of **computeds**. Computeds are **cached computations that update only when necessary**.

```python
class TodosState(ps.State):
    todos: list[Todo]
    filter: TodosFilter = "all"

    @ps.computed
    def filtered(self) -> list[Todo]:
        if self.filter == "active":
            return [t for t in self.todos if not t.completed]
        if self.filter == "completed":
            return [t for t in self.todos if t.completed]
        return self.todos
```

How it works:

- The `filtered` function doesn't run when the state is created
- The first time `state.filtered` is accessed, it executes the function
- During this function execution, Pulse detects all accessed state properties. They become the dependencies of this computed.
- Whenever a dependency changes,
- Optimizations:
  - If you have a complex graph of state properties and computeds and perform multiple updates at once, Pulse only reruns each computed once.
  - After a state update, computeds are only recaculated once they are accessed. This allows Pulse to not rerun currently unused computeds.

If you need a computed that accesses multiple states, you can also define one manually using `ps.Computed`. Generally, you should do this in `ps.setup`. Note that a computed outside a state has to be used like a function, but the same caching behavior will apply.

```python
# This is an illustrative example, not part of 04-todos.py
def setup_counters():
    counter1 = CounterState()
    counter2 = CounterState()

    @ps.computed
    def counter_sum():
        return counter1.count + counter2.count

    return counter1, counter2, counter_sum

@ps.component
def CountersWithSum():
    counter1, counter2, counter_sum = ps.setup(setup_counters)

    return ps.div(
        # Display the counters and buttons here
        ps.p(f"The sum of the counters is: {counter_sum()}")
    )
```

### 5.3. Non-reactive properties

Sometimes, you need to store something that is not reactive on a state. For instance, this could be a name for debugging purposes or a reference to another state. You could declare this like your regular reactive properties, using `name: str` or `todo_state: TodoState`, but it's good to be explicit about your intent.

In that case, the convention is to have the property's name start with an underscore, like `_name`. Otherwise, Pulse will assume the property is meant to be reactive and will complain if there is no annotation, like `name: str`, on the class.

In our todos example, this is used to communicate between `AddTodoState` and `TodosState`:

```python
class AddTodoState(ps.State):
    new_title: str = ""

    def __init__(self, todo_state: TodosState):
        self._todo_state = todo_state # OK
        # Would raise an error, as Pulse would expect something like `todo_state: TodoState`
        # self.todo_state = todo_state

    def on_add(self):
        if not self.disabled:
            self._todo_state.add_todo(self.new_title)
```

### 5.4. Global states

It's pretty common to require some kind of global state, that persists as users navigate across different pages. For example, let's say we wanted to add a details page for each TODO, where the user would be able to add a description and comments. We would need the state of all todos to persist between our todos list page and the todo details page.

However, `TodosState` is tied to the page and we currently have no way of sharing it across pages.

Besides storing our todos in a database, which will have to wait until we discuss [async](#10-async), an easy way to solve this would be to have a global `TodosState` instance.

The natural way to write it would be:

```python
todo_state = TodosState()

def TodosPage():
    # use todo_state here
    ...
```

Unfortunately, this would create a single state object that would be used across all user sessions, which is not what we want. In order to isolate the global state to a given session, we should wrap `TodosState` with `ps.global_state`.

```python
# If the state's constructor require arguments, they can be passed to ps.global_state
global_todo_state = ps.global_state(TodosState)

def TodosPage():
    todo_state = global_todo_state()
    # use todo_state in the rest of the page
    ...
```

`ps.global_state(TodosState)` creates a function which returns the global state instance for the current user session, providing automatic isolation.

> [!INFO]
> Pulse currently does not support sharing a state instance between user sessions. This is a planned feature to enable real-time collaboration, but it has not been developed and tested yet. Do not try to create a single state instance to use across sessions, you will encounter errors.

## 6. Events and callbacks

We've seen a few examples of event handlers being used to respond to user interactions. It's time we cover them properly.

Event handlers are part of Pulse's **callback** system. A **callback** is a Python function that can be called from the React app. When you pass a function as a prop to an HTML element or React component, Pulse automatically creates a corresponding JavaScript function that can be used in the client application to call into your Python function.

Callbacks can be any function, including state methods or functions recreated at every render, like a lambda. By convention, callbacks that respond to user interaction are called **event handlers** and are named starting with `on`, like `onClick` or `onChange`.

Going back to our counter example, it looks like this:

```python
class CounterState(ps.State):
    count: int = 0

    def increment(self):
        self.count += 1

    def reset(self):
        self.count = 0


@ps.component
def Counter():
    state = ps.states(CounterState)

    def decrement():
        state.count -= 1

    return ps.div(
        # `decrement` is recreated at every render, not a problem
        ps.button("Decrement", onClick=decrement),
        ps.p(f"The count is {state.count}"),
        # `increment` is a state method, works fine as well
        ps.button("Increment", onClick=state.increment)
    )
```

The event handlers above take no arguments, but most event handlers on HTML elements or React components pass in some payload. We see this in the TODOs example:

```python
ps.input(
    type="text",
    placeholder="Add a todo...",
    value=add_todo.new_title,
    onChange=lambda evt: add_todo.on_change(evt["target"]["value"]),
    className="border p-2 mr-2",
)
```

The `evt` argument contains an event payload with details about the event and target HTML element. The type of the `evt` argument is a bit complicated: `ps.ChangeEvent[ps.HTMLInputElement]`. Most of the time, if you only need a specific value from the event payload, I would suggest using a lambda to call your proper state method or handler function with the value you care about, like in the example above. That way, you get proper type checking for `evt` without having to remember the exact type to use.

Note that Pulse is able to wrap React components (see [Components](#7-components) for a quick introduction). The arguments received by event handlers on React components can be anything, from standard HTML events to simple data (a string, a date) to multiple arguments. You will have to rely on the component's documentation to learn about it.

Also, we have seen that callbacks in Pulse can decide to receive their arguments or not. The rule here is: **a Pulse callback can take no argument or all its arguments.**

## 7. Components

Another Pulse feature we have seen multiple times already is Pulse's component system. So far, we have used `@ps.component` on the render function for our pages. We have also mentioned that Pulse hooks can be called _once_ per component.

**A Pulse component is a reusable piece of user interface with persistent state and effects.**

A component can be created from any function returning Pulse elements by decorating it with `@ps.component`. Using hooks, each instance of a component can have its own internal state. Here's a very simple example using toggles ([`examples/05-toggle-component.py`](./examples/05-toggle-component.py)).

```python
"examples/05-toggle-component.py"
from pathlib import Path

import pulse as ps


class ToggleState(ps.State):
    on: bool = False

    def toggle(self):
        self.on = not self.on


@ps.component
def Toggle(label: str):
    state = ps.states(ToggleState)
    return ps.div(
        ps.button(
            f"{label}: {'ON' if state.on else 'OFF'}",
            onClick=state.toggle,
            className="px-3 py-1 rounded border",
        ),
        ps.small(
            "Enabled content…" if state.on else "", className="block text-gray-500 mt-1"
        ),
    )


@ps.component
def ToggleDemo():
    return ps.div(
        ps.h3("Reusable Toggle"),
        ps.div(Toggle(label="Wi‑Fi"), className="mb-2"),
        ps.div(Toggle(label="Bluetooth")),
    )
```

By default, a component's identity is tied to its position in the Pulse element tree. In the example above, the two toggles are identified by their position.

However, in cases where components may change position, for example when iterating over a list or when the user can reorder items, we want to preserve a component's state even if it moves around. For this, we can use **component keys**.

**Keys are used to define a component's identity and preserve its state.**

Keys can be added to a component by adding a keyword argument named `key`. It generally should default to None, as a component should be usable with or without a key.

Here is an example of a keyed vs. unkeyed scenario ([`examples/06-component-keys.py`](./examples/06-component-keys.py))

```python
"examples/06-component-keys.py"
from pathlib import Path
import pulse as ps


class ListState(ps.State):
    items: list[dict]
    new_label: str = ""

    def __init__(self):
        self.items = [
            {"id": 1, "label": "First"},
            {"id": 2, "label": "Second"},
        ]

    def prepend(self):
        next_id = max([i["id"] for i in self.items], default=0) + 1
        self.items.insert(0, {"id": next_id, "label": f"Item {next_id}"})

    def remove(self, tid: int):
        self.items = [i for i in self.items if i["id"] != tid]


class ItemState(ps.State):
    checked: bool = False
    note: str = ""


@ps.component
def Item(label: str, onRemove, key=None):
    state = ps.states(ItemState)
    return ps.div(className="flex items-center mb-2")[
        ps.input(
            type="checkbox",
            checked=state.checked,
            onChange=lambda: setattr(state, "checked", not state.checked),
            className="mr-2",
        ),
        ps.input(
            type="text",
            value=state.note,
            onChange=lambda e: setattr(state, "note", e["target"]["value"]),
            placeholder="note...",
            className="border p-1 mr-2",
        ),
        ps.span(label, className="mr-2"),
        ps.button(
            "Remove",
            onClick=onRemove,
            className="px-2 py-1 border border-red-600 text-red-600 rounded hover:bg-red-600 hover:text-white",
        ),
    ]


@ps.component
def KeysDemo():
    state = ps.states(ListState)
    # Prepend new items to the beginning to demonstrate diffing
    controls = ps.div(className="mb-4")[
        ps.button(
            "Prepend item",
            onClick=state.prepend,
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded mr-3",
        ),
    ]

    # Unkeyed: internal state will shift when items are prepended
    unkeyed = ps.div(className="p-3 border rounded mr-6")[
        ps.h4("Unkeyed (state will shift)"),
        [
            Item(
                item["label"],
                onRemove=lambda tid=item["id"]: state.remove(tid),
            )
            for item in state.items
        ],
    ]

    # Keyed: internal state stays with the same logical item
    keyed = ps.div(className="p-3 border rounded")[
        ps.h4("Keyed (state preserved)"),
        [
            Item(
                item["label"],
                onRemove=lambda tid=item["id"]: state.remove(tid),
                key=item["id"],  # critical difference
            )
            for item in state.items
        ],
    ]

    return ps.div(
        className="w-fit mx-auto h-screen flex flex-col justify-center items-start"
    )[
        ps.h3("Keys vs. No Keys"),
        controls,
        ps.div(unkeyed, keyed, className="flex"),
    ]


app = ps.App(
    routes=[ps.Route("/", KeysDemo)],
    codegen=ps.CodegenConfig(web_dir=Path(__file__).parent.parent / "pulse-web"),
)
```

Run this example, update the note and checkbox of the existing two items, and click "Prepend item".

You will notice that in the keyed version, the existing items properly shift down when a new item is added at the beginning of the list, their input and checkbox state moving with them.

In the unkeyed version, the labels shift down properly, but the checkbox and the input don't. They stay in the same position in the list.

> [!INFO]
> Keys only work at a given level in the tree. They are mostly used for list scenarios. They cannot be used to move a component to a completely different place in the UI while preserving its state.

Components can also accept children. It is recommended to define them as a variadic positional argument `*children`, as this will allow using the `Component(**props)[*children]` syntax.

```python
@ps.component
def Component(*children, key=None, title: str):
    return ps.div(
        ps.h3(title),
        *children
    )

def Page():
    # This only works if `Component` accepts a `*children` argument
    return Component(title="Section 1")[
        ps.div(...),
        ps.div(...)
    ]
```

## 8. Iterables

Talking about component keys, I mentioned that they are mostly used for lists. There are a few things to be aware of when working with lists/iterables.

The first is that you can pass an iterable of Pulse elements as a child. Pulse will automatically flatten the iterable alongside the other children (if any). If the iterable contains components, Pulse will check whether they have keys. If not, you will see a warning, as it is unintentional most of the time. Worst case, you can always use the index as the key.

```python
@ps.component
def Section(key=None, title: str, content: str):
    return ps.div(
        ps.h3(title),
        ps.p(content)
    )

def Page():
    sections = ['A', 'B', 'C']
    return ps.div(className="...")[
        # Not using a key will raise a warning
        [Section(key=title, title=title, content="...") for title in sections]
    ]
```

The second thing is that it is recommended to use the `ps.For` construct to work with iterables.

```python
ps.For(items, lambda x: ps.div(x))
```

```
Python iterables can often create subtle bugs due to [late binding semantics](https://docs.python-guide.org/writing/gotchas/#late-binding-closures).

For a demonstration, run [examples/08-iterable-late-binding.py]. Try clicking "Remove A" on the left (bad version). You should see that it removes C instead.

If you refresh and click "Remove A" on the right (good version), it will correctly remove A.

The issue is that in the bad version, all the `onClick` callbacks get a reference to `item` _after_ the iteration has ended, at which point it points to the last item.

`ps.For` mitigates this issue and will, down the line, introduce additional optimizations around rendering lists of items.

## 9. Effects

## 10. Async

## 11. Routing

- Pages take a component without arguments
- `ps.navigate`
- `ps.Outlet`
- `ps.Link`

## 12. Utilities

- `ps.route_info`: returns information about the current route (URL). Often used to get query or path parameters for dynamic routes. See [Routing](#11-routing).
- `ps.session_context`: returns a shared session context
- `ps.navigate`:
- `ps.call_api`

## 13. Common gotchas

- Component rendering order
- Rerendering philosophy
- Creating states with arguments
- Stale arguments to states (ex: callback)
- For loop

## 14. Advanced

TODO:

- Computeds in ps.setup()
- Wrapping React
- Serialization
- User sessions
- Middleware
- `ps.call_api`

## 15. Cookbook

- Using `ps.setup` for stable callbcaks
```
