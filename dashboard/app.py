from shiny.express import input, render, ui
from shiny import reactive, App
import pandas as pd
import plotly.express as px
from pathlib import Path
from shinywidgets import output_widget, render_widget
import faicons
import ridgeplot

# Load dataset
DATA_PATH = Path(__file__).parent / "GHW_HeartFailure_Readmission_Combined.csv"
df = pd.read_csv(DATA_PATH)

# Define UI
df_columns = df.columns.tolist()

ui.page_opts(title="Heart Failure Readmission Dashboard", fillable=True)

with ui.sidebar():
    ui.input_select("readmit_filter", "Filter by Readmission (30/60 Days)",
                    choices=["All", "0", "1"], selected="All")
    ui.input_select("chart_x", "Select X-axis for Chart", choices=df_columns, selected="Age")
    ui.input_select("chart_y", "Select Y-axis for Chart", choices=df_columns, selected="NT_proBNP")
    ui.input_slider("num_rows", "Number of Rows in Data Grid", min=5, max=50, value=20)

# Reactive filter based on user selection
@reactive.calc
def filtered_data():
    if input.readmit_filter() == "All":
        return df
    else:
        return df[df["Readmission_30or60Days"] == int(input.readmit_filter())]

# Main layout
with ui.layout_columns():
    ui.value_box("Total Patients", df.shape[0], showcase=faicons.icon_svg("users"))
    ui.value_box("Unique Readmissions", df[df["Readmission_30or60Days"] == 1].shape[0], showcase=faicons.icon_svg("heartbeat"))

with ui.card(full_screen=True):
    ui.card_header("Patient Data Grid")
    @render.data_frame
    def data_table():
        return filtered_data().head(input.num_rows())

with ui.card():
    ui.card_header("Readmission Scatter Plot")
    @render.plotly
    def plot():
        return px.scatter(filtered_data(), x=input.chart_x(), y=input.chart_y(), color="Readmission_30or60Days",
                          title="Scatter Plot by Selected Axes")

with ui.card():
    ui.card_header("Readmission Ridge Plot")
    @render_widget
    def ridge():
        fig = ridgeplot.ridgeplot(
            data=filtered_data(),
            x=input.chart_x(),
            y="Readmission_30or60Days",
            title=f"Distribution of {input.chart_x()} by Readmission"
        )
        return fig

# Define App
app = App(ui, server=None)
