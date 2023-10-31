import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import pandas as pd
from typing import Callable, Optional
from typing_extensions import Literal
from dash import Input, Output, State, callback, callback_context, dcc, html, dash_table
from monte_carlo import *
from oscillator import *
from bollinger_bands import *
from dual_thrust import *
from heikin_ashi import *
from parabolic_sar import *
from rsi import *
from shooting_star import *



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

class DataFrameComponent(vm.VizroBaseModel):
    """New custom component `DataFrameComponent`."""

    class Config:
        arbitrary_types_allowed = True

    type: Literal["dataframe_component"] = "dataframe_component"
    dataframe: pd.DataFrame
    function: Callable[[pd.DataFrame], pd.DataFrame]

    def build(self):
        transformed_df = self.function(self.dataframe)

        # Displaying the DataFrame using Dash's DataTable
        return html.Div([
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in transformed_df.columns],
                data=transformed_df.to_dict("records"),
            )
        ])


df = pd.read_csv("/Users/rileyoest/VS_Code/AlphaScratch/Project/Dashboard/NASDAQ/stock_data.csv")
df["DateTime"] = pd.to_datetime(df["Date"]).astype(int) / 10**9  # Convert to Unix timestamp

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
vm.Page.add_type("components", DataFrameComponent)


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

back_test = vm.Page(
    title="Back Test",
    layout=vm.Layout(grid=[[i] for i in range(33)], # range(len(components)) 
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
        # id isn't working (can't track filter changes from dfplot)
        DataFrameComponent(
            id="my_dataframe",
            dataframe=dfplot,
            function=macd_vs_awesome_stats
        ),
        vm.Card(
            text="""
            # Bollinger Bands Pattern Recognition

            * 3 bands of the Bollinger Bands are used to identify the pattern
            
            * Upper and lower bands are two standard deviations away from moving average (mid band)

            * Pattern Recognition: can test bottom W, top M, head-shoulder patterns, elliott waves, etc

            The code uses bottom W (reverse of top M)

            [TradingView](https://www.tradingview.com/wiki/Bollinger_Bands_(BB)
            )

        """,
        ),
        vm.Graph(
            id="bollinger_bands",
            figure=plot_bollinger_bands(dfplot),
        ),
        vm.Card(
            text="""
            # Dual Thrust

            * Upper and lower thresholds based on previous days' open, close, high, and low

            * When open exceeds thresholld, we take long/short based on previous upper/lower thresholds

            * No stop loss on this strategy
                - We reverse our positions when the price goes from one threshold to the other
                - Need to clear all positions by the end of day

            * Similar to London Breakout

            """,
        ), 
        vm.Graph(
            id="dual_thrust",
            figure=plot_dual_thrust(dfplot),
        ),
        vm.Card(
            text="""
            # Heikin-Ashi Candlestick

            * Alternative style of candlestick chart

            * Designed to filter out noise for momentum trading

            * Downside : Slow response
                - Should set up stop loss position accordingly so we don't get caught up in a flash crash

            [Quantiacs](https://quantiacs.com/Blog/Intro-to-Algorithmic-Trading-with-Heikin-Ashi.aspx
            )


            """,
        ),
        vm.Graph(
            id="heikin_ashi_candlesticks",
            figure=plot_heikin_ashi_candlesticks(dfplot)
        ),
        vm.Graph(
            id="heikin_ashi_profit", 
            figure=plot_heikin_ashi_profit(dfplot)
        ), 
        vm.Card(
            text="""
        
            # Paraboolic SAR

            * Indicator to identify stop and reverse of trend

            * Symbol of resistance to the price momentum

            * When SAR curve and price curve cross, trade orders are executed

            * Recursive implementation

            * Welles Wilder: creator of SAR and RSI

            [SAR](https://app.box.com/s/gbtrjuoktgyag56j6lv0)
""",
        ),
        vm.Graph(
            id="parabolic_sar",
            figure=plot_parabolic_sar(dfplot)
        ),
        vm.Card(
            text="""
            # Relative Strength Index Pattern Recognition (RSI)

            * Reflexts current strength/weakness of the stock price momentum

            * Use 14 days of smoothed average to separately calculate the intra daily uptrend and downtrend

            * Denote uptrend moving average divided by downtrend moving average as relative strength

            * Normalize relative strength by 100 which becomes an index called RSI

            * Common belief:
                - RSI > 70 ⟹ Overbought
                - RSI < 30 ⟹ Oversold

            * Could be divergence between RSI momentum and price momentum
                - Not covered in script!

            * Effectiveness of any divergence strategy on RSI is debatable

            **Pattern Recognition**

            * Unlike Bollinger Bands, we can directly look at the patterns of RSI instead of price

            * In Bollinger Bands we tested double bottom, so here we test head-shoulder

            [TradingView](https://www.tradingview.com/wiki/Relative_Strength_Index_(RSI)
            )

            ---

            **Strategies**

            * There are a couple of strategies to use RSI

            * Simplest one is overbought/oversold (this example)

            * Another one is divergence between price and RSI
                - Inventor believed bearish RSI divergence creates selling opportunity
                - His protege believed bearish divergence only occurs in a bullish trend
                - (Contradiction) Who is right? We don't know.

            * Last one is called failure swing
        """
        ),
        vm.Graph(
            id="rsi_positions",
            figure=plot_rsi_positions(dfplot)
        ),
        vm.Graph(
            id="rsi_head_shoulders", 
            figure=plot_rsi_head_shoulders(dfplot)
        ),
        vm.Graph(
            id="rsi_pattern_positions",
            figure=plot_rsi_pattern_positions(dfplot)
        ),
        vm.Graph(
            id="rsi_pattern_head_shoulder",
            figure=plot_rsi_pattern_head_shoulder(dfplot)
        ), 
        vm.Card(
            text="""
            # Shooting Star

            * Candlestick pattern

            * Long upper shadow, small lower shadow, and a small real body (shape of shooting star)

            * Indicates beginning of a bearish momentum after a price uptrend

            * Mathematics of shooting star is complicated
                - Not many candlesticks can suffice the rigid criteria of shooting star
                - In practice, most people relax the constraint on shooting star in order to trigger the signal

            * Sibling of shooting star called hammer:
                - Vertical flipped shooting star with bullish outlook
                - Close price of hammer is supposed to be higher than open price
            * Another sibling of shooting star called inverted hammer:
                - Shares same shape as shooting star, but comes with higher close price than open price and usually is an omen of price hike

            "If you see thor (with hammer), price shall soar"

            "If you see star (shooting star), price shall fall"
        """,
        ),
        vm.Graph(
            id="shooting_star_candlesticks",
            figure=plot_shooting_star_candlesticks(dfplot)
        ),
        vm.Graph(
            id="shooting_star_positions",
            figure=plot_shooting_star_positions(dfplot)
        )

    ],
    controls=[
        # Change Symbol Filter to only be able to select one stock
        vm.Filter(column="Symbol", targets=["stock_price", "volume", "monte_carlo_simulation", "monte_carlo_forcast", "awesome_positions", "macd_positions", "awesome_oscillator", "macd_oscillator", "awesome_ma", "macd_ma", "awesome_vs_macd_profit", "bollinger_bands", "dual_thrust", "heikin_ashi_candlesticks","heikin_ashi_profit", "parabolic_sar", "rsi_positions", "rsi_head_shoulders", "rsi_pattern_positions", "rsi_pattern_head_shoulder", "shooting_star_candlesticks", "shooting_star_positions"]),  # Dropdown filter for the Symbol column
        vm.Filter(
            column="DateTime",
            targets=["stock_price", "volume", "monte_carlo_simulation", "monte_carlo_forcast", "awesome_positions", "macd_positions", "awesome_oscillator", "macd_oscillator", "awesome_ma", "macd_ma", "awesome_vs_macd_profit", "bollinger_bands", "dual_thrust", "heikin_ashi_candlesticks","heikin_ashi_profit", "parabolic_sar", "rsi_positions", "rsi_head_shoulders", "rsi_pattern_positions", "rsi_pattern_head_shoulder", "shooting_star_candlesticks", "shooting_star_positions"],
            selector=TooltipNonCrossRangeSlider(), 
        ),
    ],
)

dashboard = vm.Dashboard(pages=[home_page, back_test])

if __name__ == "__main__":
    Vizro().build(dashboard).run()