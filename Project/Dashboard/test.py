

import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm
import pandas as pd
from typing import Callable
from typing_extensions import Literal
from dash import Input, Output, State, callback, callback_context, dcc, html, dash_table
from monte_carlo import *
from oscillator import *
from bollinger_bands import *
from dual_thrust import *
from parabolic_sar import *
from rsi import *
from shooting_star import *



df = pd.read_csv("/Users/rileyoest/VS_Code/AlphaScratch/Project/Dashboard/NASDAQ/stock_data.csv")
df["DateTime"] = pd.to_datetime(df["Date"]).astype(int) / 10**9  # Convert to Unix timestamp
df = df[df['Symbol'] == 'AAPL']
test_page = vm.Page(
     title="test",
     components = [
        vm.Graph(
            id="test_plot1",
            figure=plot_shooting_star_candlesticks(df),
        ),
        vm.Graph(
            id="test_plot2",
            figure=plot_shooting_star_positions(df),
        ),
        # vm.Graph(
        #     id="test_plot3",
        #     figure=plot_rsi_pattern_positions(df),
        # ),
        # vm.Graph(
        #     id="test_plot4",
        #     figure=plot_rsi_pattern_head_shoulder(df),
        # )    
     ]
     
)

dashboard = vm.Dashboard(pages=[test_page])

if __name__ == "__main__":
    Vizro().build(dashboard).run()