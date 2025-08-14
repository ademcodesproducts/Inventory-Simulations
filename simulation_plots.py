import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
import pandas as pd

class SimulationPlots:

    def __init__(self, df_inventory_data_summaries):
        self.df_inventory_data_summaries = df_inventory_data_summaries

        self.daily_metrics_df = self._create_daily_metrics_df()

    def _create_daily_metrics_df(self):
        records = []
        for _, row in self.df_inventory_data_summaries.iterrows():
            for daily_metric in row['daily_performance_metrics']:
                record = {
                    'agent': row['agent'],
                    'environment': row['environment'],
                    'service_level': row['service_level'],
                    'trial_number': row['day'],
                    'day': daily_metric['day'],
                    'demand': daily_metric['demand'],
                    'inventory': daily_metric['inventory'],
                    'fulfilled_demand': daily_metric['fulfilled_demand'],
                    'write_offs': daily_metric['write_offs'],
                }
                records.append(record)

        return pd.DataFrame(records)

    def run_dash_app(self):
        app = Dash(__name__)
        app.title = "Inventory Simulation Results"

        inventory_demand_plot = self.plot_daily_inventory_demand()
        service_level_vs_write_offs_plot = self.plot_service_level_vs_write_offs()
        fill_rate_vs_write_offs_plot = self.plot_fill_rate_vs_write_offs()
        service_level_trend_plot = self.plot_service_level_write_off_trend()

        app.layout = html.Div(
            [
                html.H1("Inventory Simulation Results"),
                dcc.Tabs(
                    [
                        dcc.Tab(
                            label="Average Inventory & Demand Over Time",
                            children=[dcc.Graph(figure=inventory_demand_plot)],
                        ),
                        dcc.Tab(
                            label="Observed Service Level vs Write-Offs",
                            children=[dcc.Graph(figure=service_level_vs_write_offs_plot)],
                        ),
                        dcc.Tab(
                            label="Fill Rate vs Write-Offs",
                            children=[dcc.Graph(figure=fill_rate_vs_write_offs_plot)],
                        ),
                        dcc.Tab(
                            label="Write-Offs vs Service Level Trend",
                            children=[dcc.Graph(figure=service_level_trend_plot)],
                        ),
                    ]
                ),
            ]
        )

        print("Running Dash app at: http://127.0.0.1:8050/")
        app.run(debug=False)

    def plot_daily_inventory_demand(self):

        grouped = (
            self.daily_metrics_df.groupby(["agent", "environment", "day"])
            .agg(
                average_inventory=("inventory", "mean"),
                average_demand=("demand", "mean"),
            )
            .reset_index()
        )

        fig = px.line(
            grouped,
            x="day",
            y="average_inventory",
            color="agent",
            line_dash="environment",
            title="Average Inventory Level Over Time",
            labels={
                "day": "Day",
                "average_inventory": "Average Inventory Level",
            }
        )

        for (agent, env), group in grouped.groupby(["agent", "environment"]):
            fig.add_trace(go.Scatter(
                x=group["day"],
                y=group["average_demand"],
                mode="lines",
                name=f"Demand | {agent} | {env}",
                line=dict(dash="dot", color="gray"),
                showlegend=True,
            ))

        fig.update_layout(
            hovermode="x unified",
        )
        return fig

    def plot_service_level_vs_write_offs(self):

        grouped = (
            self.df_inventory_data_summaries.groupby(["agent", "environment"])
            .agg(
                write_offs=("write_offs", "mean"),
                avg_service_level=("avg_service_level", "mean"),
            )
            .reset_index()
        )

        fig = px.scatter(
            grouped,
            x="write_offs",
            y="avg_service_level",
            color="agent",
            symbol="environment",
            text=grouped["agent"] + " | " + grouped["environment"],
            title="Observed Service Level vs. Total Write-Offs (Avg)",
            labels={
                "write_offs": "Total Write-Offs (Avg)",
                "avg_service_level": "Observed Service Level (Avg)",
            }
        )

        fig.update_traces(textposition="top center", marker=dict(size=10))
        fig.update_layout(height=600)
        return fig

    def plot_fill_rate_vs_write_offs(self):

        grouped = (
            self.df_inventory_data_summaries.groupby(["agent", "environment"])
            .agg(
                write_offs=("write_offs", "mean"),
                fill_rate=("fill_rate", "mean"),
            )
            .reset_index()
        )

        fig = px.scatter(
            grouped,
            x="write_offs",
            y="fill_rate",
            color="agent",
            symbol="environment",
            text=grouped["agent"] + " | " + grouped["environment"],
            title="Fill Rate vs. Total Write-Offs (Avg)",
            labels={
                "write_offs": "Total Write-Offs (Avg)",
                "fill_rate": "Fill Rate (Avg)",
            }
        )

        fig.update_traces(textposition="top center", marker=dict(size=10))
        fig.update_layout(height=600)
        return fig

    def plot_service_level_write_off_trend(self):
        grouped = (
            self.df_inventory_data_summaries.groupby(["agent", "environment", "service_level"])
            .agg(avg_service_level=("avg_service_level", "mean"),
                 avg_write_offs=("write_offs", "mean"))
            .reset_index()
        )

        fig = px.line(
            grouped,
            x="avg_service_level",
            y="avg_write_offs",
            color="agent",
            line_dash="environment",
            markers=True,
            title="Average Service Level vs Write Offs",
            labels={
                "avg_service_level": "Observed Service Level (Avg)",
                "avg_write_offs": "Write Offs (Avg)",
            }
        )

        fig.update_layout(height=600)
        return fig