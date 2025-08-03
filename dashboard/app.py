from shiny import App
from shiny.express import input, ui, render, reactive
import pandas as pd
from pathlib import Path
from datetime import datetime
import random
import plotly.express as px

# --------------------------------------------
# Read the data
# --------------------------------------------
tips_df: pd.DataFrame = pd.read_csv(Path(__file__).parent / "tips.csv")

# --------------------------------------------
# Reactive calc to filter data by selected day
# --------------------------------------------
@reactive.calc()
def filtered_data():
    selected_day = input.day()
    if selected_day == "All":
        return tips_df
    return tips_df[tips_df["day"] == selected_day]

# --------------------------------------------
# Reactive calc to simulate a live temperature
# --------------------------------------------
@reactive.calc()
def live_data():
    reactive.invalidate_later(1)
    temp = round(random.uniform(36, 39), 1)
    time = datetime.now().strftime("%H:%M:%S")
    return {"temp": temp, "time": time}

# --------------------------------------------
# Define the Shiny Express UI
# --------------------------------------------
ui.page_opts(title="Tips Dashboard - Albert Kabore", fillable=True)

# Sidebar: User Input
with ui.sidebar():
    ui.input_select("day", "Filter by Day:", ["All"] + sorted(tips_df["day"].unique().tolist()))
    ui.hr()
    ui.markdown("Use the dropdown to filter the dataset by day.")

# Main Panel
with ui.layout_columns():
    ui.value_box("Live Temp (°C)", live_data().get("temp"))
    ui.value_box("Current Time", live_data().get("time"))

with ui.card(full_screen=True):
    ui.card_header("Filtered Data Table")
    @render.data_frame
    def table():
        return filtered_data()

with ui.card():
    ui.card_header("Tip vs Total Bill (Plotly Scatter)")
    @render.plotly
    def scatter_plot():
        df = filtered_data()
        fig = px.scatter(df, x="total_bill", y="tip", color="sex", title="Tip vs Total Bill")
        return fig

# Instantiate the app
app = App()
