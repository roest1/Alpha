import vizro.plotly.express as px
from vizro.models.types import capture
from vizro import Vizro
import vizro.models as vm
import pandas as pd
from typing_extensions import Literal
from dash import Input, Output, State, callback, callback_context, dcc, html
import datetime

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

back_test = vm.Page(
    title="Back Test",
    components=[
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
            ### Go to Plot

            Plot
            """,
            href="/plot",
        ),
    
    ],
    controls=[
        vm.Filter(column="Symbol", targets=["stock_price", "volume"]),  # Dropdown filter for the Symbol column
        vm.Filter(
            column="DateTime",
            targets=["stock_price", "volume"],
            selector=TooltipNonCrossRangeSlider(), 
        ),
    ],
)

plot = vm.Page(
    title="Plot",
    components=[
        vm.Graph(
            id="stock_price_solid",
            figure=stock_price_plot(dfplot, "Date", "Close"),
        ),
        vm.Graph(
            id="volume_solid",
            figure=volume_plot(dfplot, "Date", "Volume"),
        )
    ],
)


dashboard = vm.Dashboard(pages=[home_page, back_test, plot])

if __name__ == "__main__":
    Vizro().build(dashboard).run()