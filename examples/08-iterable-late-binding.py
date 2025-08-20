from pathlib import Path
import pulse as ps


class Items(ps.State):
    items: list[dict]

    def __init__(self):
        self.items = [
            {"id": 1, "label": "A"},
            {"id": 2, "label": "B"},
            {"id": 3, "label": "C"},
        ]

    def remove(self, tid: int):
        self.items = [i for i in self.items if i["id"] != tid]


@ps.component
def LateBindingDemo():
    state = ps.states(Items)

    bad = ps.div(className="p-3 border rounded mr-6")[
        ps.h4("Bad (late-bound closures)"),
        ps.div(
            [
                ps.button(
                    f"Remove {item['label']}",
                    onClick=lambda: state.remove(
                        item["id"]  # late-bound: all point to last item
                    ),
                    className="mr-2 px-2 py-1 border rounded bg-blue-600 hover:bg-blue-700 text-white",
                )
                for item in state.items
            ]
        ),
        ps.p(f"Items: {[i['label'] for i in state.items]}"),
    ]

    good = ps.div(className="p-3 border rounded")[
        ps.h4("Good (uses ps.For)"),
        ps.div(
            ps.For(
                state.items,
                lambda item: ps.button(
                    f"Remove {item['label']}",
                    onClick=lambda: state.remove(item["id"]),
                    className="mr-2 px-2 py-1 border rounded bg-blue-600 hover:bg-blue-700 text-white",
                ),
            )
        ),
        ps.p(f"Items: {[i['label'] for i in state.items]}"),
    ]

    return ps.div(
        className="w-fit mx-auto h-screen flex flex-col justify-center items-start"
    )[
        ps.h3("Late binding in Python loops"),
        ps.div(bad, good, className="flex"),
    ]


app = ps.App(
    routes=[ps.Route("/", LateBindingDemo)],
    codegen=ps.CodegenConfig(web_dir=Path(__file__).parent.parent / "pulse-web"),
)
