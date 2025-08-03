# -----------------------------
# Imports (at the top)
# -----------------------------
from shiny import App, reactive, render, ui
from shiny.express import input, output, ui
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# Load Dataset
# -----------------------------
data_path = Path(__file__).parent / "GHW_HeartFailure_Readmission_Combined.csv"
df = pd.read_csv(data_path)

# -----------------------------
# Reactive Calc to Filter DataFrame
# -----------------------------
@reactive.calc()
def filtered_data():
    selected_gender = input.gender()
    return df[df["Gender"] == selected_gender] if selected_gender != "All" else df

# -----------------------------
# Define Shiny Express UI
# -----------------------------
ui.page_opts(title="Heart Failure Readmission Dashboard", fillable=True)

# Sidebar
with ui.sidebar(open="open"):
    ui.input_select(
        "gender",
        "Select Gender",
        choices=["All"] + sorted(df["Gender"].dropna().unique().tolist()),
        selected="All"
    )

# -----------------------------
# Main Section - UI Cards, Value Boxes, Data Grid, Chart
# -----------------------------
with ui.layout_columns():
    @output
    @render.text
    def total_patients():
        return f"Total Patients: {len(filtered_data())}"

    @output
    @render.text
    def readmission_rate():
        rate = filtered_data()["Readmitted"].mean() * 100
        return f"Readmission Rate: {rate:.2f}%"

with ui.layout_columns():
    @output
    @render.data_frame
    def data_table():
        return filtered_data().head(10)

    @output
    @render.plotly
    def readmission_by_age():
        fig = px.histogram(filtered_data(), x="Age", color="Readmitted", barmode="group")
        fig.update_layout(title="Readmission by Age")
        return fig

# -----------------------------
# Create App
# -----------------------------
app = App()