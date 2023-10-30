import vizro.plotly.express as px
from vizro.models.types import capture
from vizro import Vizro
import vizro.models as vm
import pandas as pd
from typing_extensions import Literal
from dash import Input, Output, State, callback, callback_context, dcc, html, dash_table
from monte_carlo import *
from oscillator import *
from typing import List, Any, Callable


df = pd.read_csv("/Users/rileyoest/VS_Code/AlphaScratch/Project/Dashboard/NASDAQ/stock_data.csv")
df["DateTime"] = pd.to_datetime(df["Date"]).astype(int) / 10**9  # Convert to Unix timestamp


"""
Need to update toolkit in slider to display date range
"""
class TooltipNonCrossRangeSlider(vm.RangeSlider):
    """Custom numeric multi-selector `TooltipNonCrossRangeSlider`."""

    type: Literal["other_range_slider"] = "other_range_slider" 

    def build(self):  
        value = self.value or [self.min, self.max]  # type: ignore[list-item]
        
        output = [
            Output(f"{self.id}_start_value", "value"), 
            Output(f"{self.id}_end_value", "value"),
            Output(self.id, "value"),
            Output(f"temp-store-range_slider-{self.id}", "data"),
        ]
        input = [
            Input(f"{self.id}_start_value", "value"),
            Input(f"{self.id}_end_value", "value"),
            Input(self.id, "value"),
            State(f"temp-store-range_slider-{self.id}", "data"),
        ]

        @callback(output=output, inputs=input)
        def update_slider_values(start, end, slider, input_store):
            trigger_id = callback_context.triggered_id
            if trigger_id == f"{self.id}_start_value" or trigger_id == f"{self.id}_end_value":
                start_text_value, end_text_value = start, end
            elif trigger_id == self.id:
                start_text_value, end_text_value = slider
            else:
                start_text_value, end_text_value = input_store if input_store is not None else value

            start_value = min(start_text_value, end_text_value)
            end_value = max(start_text_value, end_text_value)
            start_value = max(self.min, start_value)
            end_value = min(self.max, end_value)
            
            slider_value = [start_value, end_value]
            
            start_date = pd.to_datetime(start_value, unit='s').strftime('%Y-%m-%d')
            end_date = pd.to_datetime(end_value, unit='s').strftime('%Y-%m-%d')

            return start_date, end_date, slider_value, (start_value, end_value)

        return html.Div(
            [
                html.P(self.title, id="range_slider_title") if self.title else None,
                html.Div(
                    [
                        dcc.RangeSlider(
                            id=self.id,
                            min=self.min,
                            max=self.max,
                            step=self.step,
                            #marks={},
                            marks=self.marks,
                            className="range_slider_control" if self.step else "range_slider_control_no_space",
                            value=value,
                            persistence=True,
                            allowCross=False, 
                            tooltip={"placement": "bottom", "always_visible": True}, 
                        ),
                        html.Div(
                            [
                                dcc.Input(
                                    id=f"{self.id}_start_value",
                                    type='text',
                                    placeholder="start",
                                    readOnly=True,
                                    className="slider_input_field_left"
                                    if self.step
                                    else "slider_input_field_no_space_left",
                                    value="",
                                    size="100px",
                                    persistence=True,
                                ),
                                dcc.Input(
                                    id=f"{self.id}_end_value",
                                    type='text',
                                    placeholder="end",
                                    readOnly=True,
                                    className="slider_input_field_right"
                                    if self.step
                                    else "slider_input_field_no_space_right",
                                    value="",
                                    size="100px",
                                    persistence=True,
                                ),
                                dcc.Store(id=f"temp-store-range_slider-{self.id}", storage_type="local"),
                            ],
                            className="slider_input_container",
                        ),
                    ],
                    className="range_slider_inner_container",
                ),
            ],
            className="selector_container",
        )


# DFFunction = Callable[[pd.DataFrame], pd.DataFrame]

# class DataFrameDisplay(vm.VizroBaseModel):
#     """New custom component `DataFrameDisplay`."""

#     type: Literal["dataframedisplay"] = "dataframedisplay"
#     data: Any
#     function: DFFunction

#     @property
#     def dataframe(self) -> pd.DataFrame:
#         # Check if data is already a DataFrame. If not, try to convert it to one.
#         if isinstance(self.data, pd.DataFrame):
#             df = self.data
#         else:
#             df = pd.DataFrame(self.data)
#         return self.function(df)

#     def build(self):
#         return dash_table.DataTable(
#             columns=[{"name": col, "id": col} for col in self.dataframe.columns],
#             data=self.dataframe.to_dict("records"),
#         )


home_page = vm.Page(
    title="Alpha Generator",
    components=[
        vm.Card(
            text="""
            ### Back Test

            Back Testing
            """,
            href="/back-test",
        ),
        vm.Card(
            text="""

            ### Live Trade

            Live Trading
            """,
            href="/live-trade",
        ),
    ],
)

def stock_price_plot(df, x, y, symbol=None):
    if symbol:
        df = df[df['Symbol'] == symbol]
    return px.line(df, x=x, y=y)

def volume_plot(df, x, y, symbol=None):
    if symbol:
        df = df[df['Symbol'] == symbol]
    return px.line(df, x=x, y=y)

def select_range(df, start, end, symbol=None):
    if symbol:
        df = df[df['Symbol'] == symbol]
    return df[(df["Date"] >= start) & (df["Date"] <= end)]

dfplot = select_range(df, df['Date'].min(), df['Date'].max())

vm.Filter.add_type("selector", TooltipNonCrossRangeSlider)
#vm.Page.add_type("components", DataFrameDisplay)

back_test = vm.Page(
    title="Back Test",
    layout=vm.Layout(grid=[[i] for i in range(15)], # range(len(components))
                     row_min_height="350px"),
    components=[
        vm.Card(
            text="""
            # Select Stock & Date Range
            """,
        ),
        vm.Graph(
            id="stock_price",
            figure=stock_price_plot(dfplot, "Date", "Close"),
        ),
        vm.Graph(
            id="volume",
            figure=volume_plot(dfplot, "Date", "Volume"),
        ),
        vm.Card(
            text="""
            # Indicators

            """,
        ),
        vm.Card(
            text="""
            # Monte Carlo

            * Most ML applications in trading are leaned towards analytics rather than prediction

            * Monte Carlo refers to the computer simulation of massive amounts of random events
                - Extremely powerful in studies of stochastic processes

            * Cannot accurately predict the direction of the momentum under extreme events (ie: 2008 financial crisis)

            * Weakness of Monte Carlo is you can't predict something in the future if it has never happened in the past

            """,
        ),
        vm.Graph(
            id="monte_carlo_simulation",
            figure=monte_carlo_simulation(dfplot),
        ),
        vm.Graph(
            id="monte_carlo_forcast",
            figure=monte_carlo_forecast(dfplot),
        ),
        # vm.Graph(
        #     id="monte_carlo_test",
        #     figure=monte_carlo_test(dfplot),
        # ),
        vm.Card(
            text="""
            # Awesome Oscillator (upgraded MACD)

            * Momentum strategy focussed on moving average

            * Instead of taking moving average on close price, it is derived from the mean of high and low prices

            * similar to MACD oscillator, it takes both short and long term moving averages to construct.

            * Various strategies to generate signals, such as traditional moving average divergence, twin peaks (W pattern), and saucer

            * We will use saucer in this example

            * Saucer has the power to beat the slow response of traditional divergence
                - Faster response doesn't guarantee a less risky or more profitable outcome

            * We will use MACD oscillator as control group to test if the awesome oscillator outperforms it

            [Awesome Oscillator](https://www.tradingview.com/support/solutions/43000501826-awesome-oscillator-ao/)

            """,
        ),
        vm.Graph(
            id="awesome_positions",
            figure=plot_awesome_positions_signals(dfplot),
        ),
        vm.Graph(
            id="macd_positions",
            figure=plot_macd_positions_signals(dfplot),
        ),
        vm.Graph(
            id="awesome_oscillator",
            figure=plot_awesome_oscillator_bar(dfplot),
        ),
        vm.Graph(
            id="macd_oscillator",
            figure=plot_macd_oscillator_bar(dfplot),
        ),
        vm.Graph(
            id="awesome_ma",
            figure=plot_awesome_ma(dfplot),
        ),
        vm.Graph(
            id="macd_ma",
            figure=plot_macd_ma(dfplot),
        ), 
        vm.Graph(
            id="awesome_vs_macd_profit",
            figure=plot_macd_vs_awesome_profit(dfplot),
        ), 
        # DataFrameDisplay(
        #     id="my_dataframe_display",
        #     data=dfplot,
        #     function=macd_vs_awesome_stats,
        # )
    ],
    controls=[
        # Change Symbol Filter to only be able to select one stock
        vm.Filter(column="Symbol", targets=["stock_price", "volume", "monte_carlo_simulation", "monte_carlo_forcast", "awesome_positions", "macd_positions", "awesome_oscillator", "macd_oscillator", "awesome_ma", "macd_ma", "awesome_vs_macd_profit"]),  # Dropdown filter for the Symbol column
        vm.Filter(
            column="DateTime",
            targets=["stock_price", "volume", "monte_carlo_simulation", "monte_carlo_forcast", "awesome_positions", "macd_positions", "awesome_oscillator", "macd_oscillator", "awesome_ma", "macd_ma", "awesome_vs_macd_profit"],
            selector=TooltipNonCrossRangeSlider(), 
        ),
    ],
)

dashboard = vm.Dashboard(pages=[home_page, back_test])

if __name__ == "__main__":
    Vizro().build(dashboard).run()