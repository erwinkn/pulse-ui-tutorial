import pulse as ps


@ps.component
def home():
    return ps.div("Welcome to Pulse!")


app = ps.App(
    routes=[ps.Route("/", home)],
)
