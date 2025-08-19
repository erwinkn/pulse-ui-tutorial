# The Pulse tutorial

Welcome to the Pulse tutorial! In this guide, we'll build a complete task management application that covers all the key concepts of the Pulse framework.

## What We're Building

Our task manager will feature:

- ✅ Task creation with categories
- ✅ Real-time updates and state synchronization
- ✅ Change history tracking for every modification
- ✅ Dynamic routing with individual task pages
- ✅ Query-based data loading with caching
- ✅ Component-based architecture with reusable pieces

---

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

## 4. Hooks {#hooks}

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

Components are functions decorated with `@ps.component`. We will discuss them in the [Components](#6-components) section.

This rule illustrates that the purpose of hooks is to **give you a way to do something exactly once, when a component first renders**.

In practice, you could do everything with `ps.setup`: create your states, set up your effects, initialize something, etc... `ps.states` and `ps.effects` are convenience hooks for common requirements.

### 4.3. Usage

Let's understand how to use hooks by looking at an example. I will not use `ps.effects` here, as it will be introduced in [Effects](#7-effects).

<details>
<summary>Hooks example ([`examples/03-hooks.py`](./examples/03-hooks.py))</summary>

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

</details>

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
  - This is useful if you have more complex initialization needs. See the [Cookbook](#13-cookbook) for usage examples.

## 5. State (part II)

Now that we understand how hooks work, everything in the first state demo ([`examples/02-counter.py`](./examples/02-counter.py)) should be clear. States are one of Pulse's central features and they have more features we haven't discussed yet, so let's explore them.

We're going to use a TODO list example to guide us through this section.

### 5.1. Reactive collections


### 5.2. Computeds

### 5.3. Non-reactive properties

### 5.4. Global states

## 6. Events and event handlers

## 7. Components

- Basics
- State preservation
- Keys + iterables
  -> Swap demo is good
- For loop and gotchas

## 8. Effects

## 9. Async

## 10. Routing

- `ps.navigate`
- `ps.Outlet`
- `ps.Link`

## 11. Utilities

- `ps.route_info`: returns information about the current route (URL). Often used to get query or path parameters for dynamic routes. See [Routing](#9-routing).
- `ps.session_context`: returns a shared session context
- `ps.navigate`:
- `ps.call_api`

## 12. Common gotchas

- Component rendering order
- Rerendering philosophy
- Creating states with arguments
- Stale arguments to states (ex: callback)
- For loop

## 13. Advanced features

TODO:

- User sessions
- Middleware
- `ps.call_api`

## 14. Cookbook

- Using `ps.setup` for stable callbcaks
