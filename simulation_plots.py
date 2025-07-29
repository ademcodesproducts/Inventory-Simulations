from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

class SimulationPlots:
    def __init__(self, inventory_data, sl_writeoff_data):
        self.inventory_data = pd.DataFrame(inventory_data)
        self.sl_writeoff_data = pd.DataFrame(sl_writeoff_data)

    def run_dash_app(self):
        app = Dash(__name__)
        app.title = "Inventory Simulation Results"

        inventory_fig = self.create_inventory_figure()
        writeoff_vs_sl_fig = self.create_writeoff_vs_service_level_figure()
        writeoff_vs_fillrate_fig = self.create_writeoff_vs_fillrate_figure()

        app.layout = html.Div([
            html.H1("Inventory Simulation Results"),
            dcc.Tabs([
                dcc.Tab(label='Inventory Levels', children=[
                    dcc.Graph(figure=inventory_fig)
                ]),
                dcc.Tab(label='Cycle Service Level vs Write-Offs', children=[
                    dcc.Graph(figure=writeoff_vs_sl_fig)
                ]),
                dcc.Tab(label='Fill Rate vs Write-Offs', children=[
                    dcc.Graph(figure=writeoff_vs_fillrate_fig)
                ])
            ])
        ])

        print("Running Dash app at: http://127.0.0.1:8050/")
        app.run(debug=True)

    def create_inventory_figure(self):
        df = self.inventory_data

        grouped = df.groupby(["Agent", "Environment", "Day"]).agg(
            InventoryLevel=('InventoryLevel', 'mean'),
            ActualDemand=('ActualDemand', 'mean')
        ).reset_index()

        fig = px.line(
            grouped,
            x="Day",
            y="InventoryLevel",
            color="Agent",
            line_dash="Environment",
            title="Average Inventory Level Over Time"
        )

        # Scatter plot as line for actual demand
        for (agent, env), group in grouped.groupby(["Agent", "Environment"]):
            fig.add_scatter(
                x=group["Day"],
                y=group["ActualDemand"],
                mode="lines",
                name=f"Demand | {agent} | {env}",
                line=dict(dash="dot", color="gray"),
                showlegend=True
            )

        fig.update_layout(
            xaxis_title="Day",
            yaxis_title="Average Inventory Level",
            hovermode="x unified"
        )
        return fig

    def create_writeoff_vs_service_level_figure(self):
        df = self.sl_writeoff_data

        grouped = df.groupby(["Agent", "Environment"]).agg({
            "Write_Offs": "mean",
            "Cycle_Service_Level": "mean"
        }).reset_index()

        grouped["Label"] = grouped["Agent"] + " | " + grouped["Environment"]

        fig = px.scatter(
            grouped,
            x="Write_Offs",
            y="Cycle_Service_Level",
            color="Agent",
            symbol="Environment",
            text="Label",
            title="Cycle Service Level vs. Total Write-Offs",
        )

        fig.update_traces(textposition='top center', marker=dict(size=10))
        fig.update_layout(
            xaxis_title="Total Write-Offs (Avg)",
            yaxis_title="Cycle Service Level (Avg)",
            height=600
        )
        return fig

    def create_writeoff_vs_fillrate_figure(self):
        df = self.sl_writeoff_data

        grouped = df.groupby(["Agent", "Environment"]).agg({
            "Write_Offs": "mean",
            "Fill_Rate": "mean"
        }).reset_index()

        grouped["Label"] = grouped["Agent"] + " | " + grouped["Environment"]

        fig = px.scatter(
            grouped,
            x="Write_Offs",
            y="Fill_Rate",
            color="Agent",
            symbol="Environment",
            text="Label",
            title="Fill Rate vs. Total Write-Offs",
        )

        fig.update_traces(textposition='top center', marker=dict(size=10))
        fig.update_layout(
            xaxis_title="Total Write-Offs (Avg)",
            yaxis_title="Fill Rate (Avg)",
            height=600
        )
        return fig
