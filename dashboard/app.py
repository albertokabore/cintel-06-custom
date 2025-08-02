from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.express as px
import faicons as fa
from datetime import datetime
import random
from pathlib import Path

# ------------------------------
# Constants
# ------------------------------
UPDATE_INTERVAL_SECS = 1

# ------------------------------
# Load dataset
# ------------------------------
TIPS_PATH = Path(__file__).parent / "tips.csv"
tips = pd.read_csv(TIPS_PATH)
bill_rng = (tips.total_bill.min(), tips.total_bill.max())

# ------------------------------
# Icons
# ------------------------------
ICONS = {
    "user": fa.icon_svg("user", fill="currentColor"),
    "wallet": fa.icon_svg("wallet"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis")
}

# ------------------------------
# Reactive live tip generator
# ------------------------------
@reactive.calc
def live_tip():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)
    tip = round(random.uniform(10, 30), 2)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return tip, time

# ------------------------------
# Reactive filtered data
# ------------------------------
@reactive.calc
def filtered_data():
    df = tips.copy()
    min_bill, max_bill = input.bill()
    df = df[(df["total_bill"] >= min_bill) & (df["total_bill"] <= max_bill)]

    selected_times = input.times()
    if selected_times:
        df = df[df["time"].isin(selected_times)]

    return df

# ------------------------------
# UI Layout
# ------------------------------
ui.page_opts(title="Albert Kabore - Restaurant Tipping Dashboard", fillable=True)

with ui.sidebar():
    ui.input_slider("bill", "Bill amount", min=bill_rng[0], max=bill_rng[1], value=bill_rng, step=1)
    ui.input_checkbox_group("times", "Food service", choices=["Lunch", "Dinner"], selected=["Lunch", "Dinner"])
    ui.input_action_button("reset_btn", "Reset filter")

with ui.layout_columns():
    ui.value_box("Total tippers", tips.shape[0], showcase=ICONS["user"])
    ui.value_box("Average tip", f"{round(tips.tip.mean()/tips.total_bill.mean()*100, 1)}%", showcase=ICONS["wallet"])
    ui.value_box("Average bill", f"${round(tips.total_bill.mean(), 2)}", showcase=ICONS["currency-dollar"])

    tip_val, tip_time = live_tip()
    ui.value_box("Live Tip Update", f"Live Tip: {tip_val} at {tip_time}", showcase=ICONS["ellipsis"])

with ui.card():
    ui.card_header("Tips data")
    @render.data_frame
    def show_table():
        return filtered_data()

with ui.card():
    ui.card_header("Total bill vs tip")
    @render.plotly
    def scatter_plot():
        df = filtered_data()
        return px.scatter(df, x="total_bill", y="tip", title="Total bill vs tip", trendline="ols")

with ui.card():
    ui.card_header("Tip percentages")
    @render.plotly
    def tip_hist():
        df = filtered_data().copy()
        df["percent"] = (df["tip"] / df["total_bill"] * 100).round(1)
        return px.histogram(df, x="percent", color="day", barmode="group", title="Distribution of Tip Percentage")

# ------------------------------
# App
# ------------------------------
app = App(ui, server=None)
