import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

# Graphs #
"""
df = px.data.iris()

page = vm.Page(
    title="My first dashboard",
    components=[
        vm.Graph(id="scatter_chart", figure=px.scatter(df, x="sepal_length", y="petal_width", color="species")),
        vm.Graph(id="hist_chart", figure=px.histogram(df, x="sepal_width", color="species")),
    ],
    controls=[
        vm.Filter(column="species", selector=vm.Dropdown(value=["ALL"])),
    ],
)

dashboard = vm.Dashboard(pages=[page])

Vizro().build(dashboard).run()
"""

"""
df = px.data.iris()

page1 = vm.Page(
    title="My first page",
    components=[
        vm.Graph(
            id="my_chart",
            figure=px.scatter_matrix(
                df, dimensions=["sepal_length", "sepal_width", "petal_length", "petal_width"], color="species"
            ),
        ),
    ],
    controls=[vm.Filter(column="species", selector=vm.Dropdown(title="Species"))],
)

#dashboard = vm.Dashboard(pages=[page1])

#Vizro().build(dashboard).run()
"""
#############

# Cards #
# uses markdown

# page2 = vm.Page(
#     title="Customizing Text",
#     components=[
#         vm.Card(
#             text="""
#                 # Header level 1 <h1>

#                 ## Header level 2 <h2>

#                 ### Header level 3 <h3>

#                 #### Header level 4 <h4>
#             """,
#         ),
#         vm.Card(
#             text="""
#                  ### Paragraphs
#                  Commodi repudiandae consequuntur voluptatum laborum numquam blanditiis harum quisquam eius sed odit.

#                  Fugiat iusto fuga praesentium option, eaque rerum! Provident similique accusantium nemo autem.

#                  Obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam nihil, eveniet aliquid.

#                  Culpa officia aut! Impedit sit sunt quaerat, odit, tenetur error, harum nesciunt ipsum debitis quas.
#             """,
#         ),
#         vm.Card(
#             text="""
#                 ### Block Quotes

#                 >
#                 > A block quote is a long quotation, indented to create a separate block of text.
#                 >
#             """,
#         ),
#         vm.Card(
#             text="""
#                 ### Lists

#                 * Item A
#                     * Sub Item 1
#                     * Sub Item 2
#                 * Item B
#             """,
#         ),
#         vm.Card(
#             text="""
#                 ### Emphasis

#                 This word will be *italic*

#                 This word will be **bold**

#                 This word will be _**bold and italic**_
#             """,
#         ),
#     ],
# )


# dashboard = vm.Dashboard(pages=[page1, page2])

# Vizro().build(dashboard).run()

##############

# df = px.data.gapminder()
# gapminder_data = (
#         df.groupby(by=["continent", "year"]).
#             agg({"lifeExp": "mean", "pop": "sum", "gdpPercap": "mean"}).reset_index()
#     )

# first_page = vm.Page(
#     title="First Page",
#     #layout=vm.Layout(grid=[[0, 0], [1, 2], [1, 2], [1, 2]]),
#     components=[
#         vm.Card(
#             text="""
#                 # First dashboard page
#                 This pages shows the inclusion of markdown text in a page and how components
#                 can be structured using Layout.
#             """,
#         ),
#         vm.Graph(
#             id="box_cont",
#             figure=px.box(gapminder_data, x="continent", y="lifeExp", color="continent",
#                             labels={"lifeExp": "Life Expectancy", "continent":"Continent"}),
#         ),
#         vm.Graph(
#             id="line_gdp",
#             figure=px.line(gapminder_data, x="year", y="gdpPercap", color="continent",
#                             labels={"year": "Year", "continent": "Continent",
#                             "gdpPercap":"GDP Per Cap"}),
#         ),

#     ],
#     controls=[
#         vm.Filter(column="continent", targets=["box_cont", "line_gdp"]),
#     ],
# )

# dashboard = vm.Dashboard(pages=[first_page])
# Vizro().build(dashboard).run()

# df = px.data.gapminder()
# gapminder_data = (
#         df.groupby(by=["continent", "year"]).
#             agg({"lifeExp": "mean", "pop": "sum", "gdpPercap": "mean"}).reset_index()
#     )
# first_page = vm.Page(
#     title="First Page",
#     layout=vm.Layout(grid=[[0, 0], [1, 2], [1, 2], [1, 2]]),
#     components=[
#         vm.Card(
#             text="""
#                 # First dashboard page
#                 This pages shows the inclusion of markdown text in a page and how components
#                 can be structured using Layout.
#             """,
#         ),
#         vm.Graph(
#             id="box_cont",
#             figure=px.box(gapminder_data, x="continent", y="lifeExp", color="continent",
#                             labels={"lifeExp": "Life Expectancy", "continent":"Continent"}),
#         ),
#         vm.Graph(
#             id="line_gdp",
#             figure=px.line(gapminder_data, x="year", y="gdpPercap", color="continent",
#                             labels={"year": "Year", "continent": "Continent",
#                             "gdpPercap":"GDP Per Cap"}),
#             ),
#     ],
#     controls=[
#         vm.Filter(column="continent", targets=["box_cont", "line_gdp"]),
#     ],
# )

# iris_data = px.data.iris()
# second_page = vm.Page(
#     title="Second Page",
#     components=[
#         vm.Graph(
#             id="scatter_iris",
#             figure=px.scatter(iris_data, x="sepal_width", y="sepal_length", color="species",
#                 color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
#                 labels={"sepal_width": "Sepal Width", "sepal_length": "Sepal Length",
#                         "species": "Species"},
#             ),
#         ),
#         vm.Graph(
#             id="hist_iris",
#             figure=px.histogram(iris_data, x="sepal_width", color="species",
#                 color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
#                 labels={"sepal_width": "Sepal Width", "count": "Count",
#                         "species": "Species"},
#             ),
#         ),
#     ],
#     controls=[
#         vm.Parameter(
#             targets=["scatter_iris.color_discrete_map.virginica",
#                         "hist_iris.color_discrete_map.virginica"],
#             selector=vm.Dropdown(
#                 options=["#ff5267", "#3949ab"], multi=False, value="#3949ab", title="Color Virginica"),
#             ),
#         vm.Parameter(
#             targets=["scatter_iris.opacity", "hist_iris.opacity"],
#             selector=vm.Slider(min=0, max=1, value=0.8, title="Opacity"),
#         ),
#     ],
# )

# dashboard = vm.Dashboard(pages=[first_page,second_page])
# Vizro().build(dashboard).run()

"""
Create final dashboard

"""

home_page = vm.Page(
    title="Homepage",
    components=[
        vm.Card(
            text="""
            ![](assets/images/icons/content/collections.svg#icon-top)

            ### First Page

            Exemplary first dashboard page.
            """,
            href="/first-page",
        ),
        vm.Card(
            text="""
            ![](assets/images/icons/content/features.svg#icon-top)

            ### Second Page

            Exemplary second dashboard page.
            """,
            href="/second-page",
        ),
    ],
)

df = px.data.gapminder()
gapminder_data = (
        df.groupby(by=["continent", "year"]).
            agg({"lifeExp": "mean", "pop": "sum", "gdpPercap": "mean"}).reset_index()
    )
first_page = vm.Page(
    title="First Page",
    layout=vm.Layout(grid=[[0, 0], [1, 2], [1, 2], [1, 2]]),
    components=[
        vm.Card(
            text="""
                # First dashboard page
                This pages shows the inclusion of markdown text in a page and how components
                can be structured using Layout.
            """,
        ),
        vm.Graph(
            id="box_cont",
            figure=px.box(gapminder_data, x="continent", y="lifeExp", color="continent",
                            labels={"lifeExp": "Life Expectancy", "continent":"Continent"}),
        ),
        vm.Graph(
            id="line_gdp",
            figure=px.line(gapminder_data, x="year", y="gdpPercap", color="continent",
                            labels={"year": "Year", "continent": "Continent",
                            "gdpPercap":"GDP Per Cap"}),
            ),
    ],
    controls=[
        vm.Filter(column="continent", targets=["box_cont", "line_gdp"]),
    ],
)

iris_data = px.data.iris()
second_page = vm.Page(
    title="Second Page",
    components=[
        vm.Graph(
            id="scatter_iris",
            figure=px.scatter(iris_data, x="sepal_width", y="sepal_length", color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                labels={"sepal_width": "Sepal Width", "sepal_length": "Sepal Length",
                        "species": "Species"},
            ),
        ),
        vm.Graph(
            id="hist_iris",
            figure=px.histogram(iris_data, x="sepal_width", color="species",
                color_discrete_map={"setosa": "#00b4ff", "versicolor": "#ff9222"},
                labels={"sepal_width": "Sepal Width", "count": "Count",
                        "species": "Species"},
            ),
        ),
    ],
    controls=[
        vm.Parameter(
            targets=["scatter_iris.color_discrete_map.virginica",
                        "hist_iris.color_discrete_map.virginica"],
            selector=vm.Dropdown(
                options=["#ff5267", "#3949ab"], multi=False, value="#3949ab", title="Color Virginica"),
            ),
        vm.Parameter(
            targets=["scatter_iris.opacity", "hist_iris.opacity"],
            selector=vm.Slider(min=0, max=1, value=0.8, title="Opacity"),
        ),
    ],
)

dashboard = vm.Dashboard(pages=[home_page, first_page, second_page])
Vizro().build(dashboard).run()

