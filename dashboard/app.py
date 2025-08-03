from shiny import App, reactive, render, ui
from shinywidgets import render_plotly, output_widget
import pandas as pd
import seaborn as sns
import random
from datetime import datetime
import plotly.express as px

# --------------------------------------------
# Load the tips dataset
# --------------------------------------------
tips_df: pd.DataFrame = sns.load_dataset("tips")

# --------------------------------------------
# UI Layout
# --------------------------------------------
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("day", "Filter by Day:", ["All"] + sorted(tips_df["day"].unique().tolist())),
        ui.hr(),
        ui.markdown("Use the dropdown menu to filter data by day of the week."),
        open="desktop"
    ),
    ui.layout_columns(
        ui.value_box("Live Temperature (°C)", ui.output_ui("live_temp")),
        ui.value_box("Current Time", ui.output_ui("live_time")),
    ),
    ui.card(
        ui.card_header("Filtered Tips Data"),
        ui.output_data_frame("table"),
        full_screen=True
    ),
    ui.card(
        ui.card_header("Tip vs Total Bill (Plotly Scatter)"),
        output_widget("scatter_plot")  # ✅ Use this instead of ui.output_plot
    ),
    title="Tips Dashboard - Albert Kabore",
    fillable=True
)

# --------------------------------------------
# Server Logic
# --------------------------------------------
def server(input, output, session):

    @reactive.calc()
    def filtered_data():
        selected_day = input.day()
        if selected_day == "All":
            return tips_df
        return tips_df[tips_df["day"] == selected_day]

    @reactive.calc()
    def live_data():
        reactive.invalidate_later(1)
        temp = round(random.uniform(36, 39), 1)
        time = datetime.now().strftime("%H:%M:%S")
        return {"temp": temp, "time": time}

    @output
    @render.ui
    def live_temp():
        return f"{live_data()['temp']}"

    @output
    @render.ui
    def live_time():
        return f"{live_data()['time']}"

    @output
    @render.data_frame
    def table():
        return render.DataGrid(filtered_data())

    @output
    @render_plotly
    def scatter_plot():
        df = filtered_data()
        fig = px.scatter(df, x="total_bill", y="tip", color="sex", title="Tip vs Total Bill")
        return fig

# --------------------------------------------
# Create the App
# --------------------------------------------
app = App(app_ui, server)
