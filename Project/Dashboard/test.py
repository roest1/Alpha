from vizro import Vizro
import vizro.plotly.express as px
import vizro.models as vm

iris = px.data.iris()

page = vm.Page(
    title="My first page",
    components=[
        vm.Graph(
            id="scatter_chart",
            figure=px.scatter(iris, title="My scatter chart", x="sepal_length", y="petal_width", color="species"),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["scatter_chart.title"],
            selector=vm.Dropdown(
                options=["My scatter chart", "A better title!", "Another title..."],
                multi=False,
            ),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
