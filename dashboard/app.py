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
    gender = input.gender()
    if gender == "All":
        return df
    return df[df["Gender"] == gender]

# -----------------------------
# Define Shiny Express UI
# -----------------------------
ui.page_opts(title="Heart Failure Readmission Dashboard", fillable=True)

# Sidebar
with ui.sidebar(open="open"):
    ui.input_select(
        "gender",
        "Filter by Gender",
        choices=["All"] + sorted(df["Gender"].dropna().unique().tolist()),
        selected="All"
    )

# -----------------------------
# Main Section - UI Cards, Value Boxes, Data Table, Plotly Chart
# -----------------------------
with ui.layout_columns():
    @output
    @render.text
    def total_patients():
        return f"🧍 Total Patients: {len(filtered_data())}"

    @output
    @render.text
    def readmission_rate():
        readmitted_col = filtered_data()["Readmitted"]
        if readmitted_col.dtype == "bool" or readmitted_col.nunique() == 2:
            rate = readmitted_col.mean() * 100
            return f"🔁 Readmission Rate: {rate:.2f}%"
        return "Invalid 'Readmitted' column format."

with ui.layout_columns():
    @output
    @render.data_frame
    def data_grid():
        return filtered_data().head(10)

    @output
    @render.plotly
    def plot_readmission_by_age():
        fig = px.histogram(
            filtered_data(),
            x="Age",
            color="Readmitted",
            barmode="group",
            title="Readmission by Age"
        )
        return fig

# -----------------------------
# Create App
# -----------------------------
app = App()
