import ciw
import numpy as np
import pandas as pd

from safety_stock_experimentations import simulation_plots
from safety_stock_experimentations.agent import (
    ForecastAgent,
    MonteCarloAgent,
    SafetyStockAgent,
    BaseAgent,
)
from safety_stock_experimentations.config import HISTO_DAYS, LEAD_TIME, N_SIMULATIONS
from safety_stock_experimentations.demand_distribution import (
    SingleGammaLowVariance,
    GammaGammaHighVariance,
    GammaPoisson,
)
from safety_stock_experimentations.simulator import Simulator

np.random.seed(11)
ciw.random.seed(11)

print("Simulation of Agents over different Environments and Service Levels")

service_levels_list = [0.90, 0.92, 0.94, 0.95, 0.96, 0.98]

environment_configs = {
    # 0: {"name": "90/10 Gamma/Poisson", "class": GammaPoisson},
    # 1: {"name": "50/50 Gamma(mu=20)/Gamma(mu=200)", "class": GammaGammaHighVariance},
    2: {"name": "Gamma", "class": SingleGammaLowVariance},
}

agent_configs = {
    0: {"name": "Historical Demand Agent", "class": BaseAgent},
    1: {"name": "Safety Stock Agent", "class": SafetyStockAgent},
    2: {"name": "Forecast Agent", "class": ForecastAgent},
    3: {"name": "Monte Carlo Agent", "class": MonteCarloAgent},
}

inventory_data_summaries = []

for env_info in environment_configs.values():
    environments = [env_info["class"]().execute() for _ in range(N_SIMULATIONS)]

    for service_level in service_levels_list:

        for trial_number in range(N_SIMULATIONS):
            environment = environments[trial_number]

            for agent_info in agent_configs.values():
                selected_agent = agent_info["class"](environment, service_level)
                sim = Simulator(selected_agent, environment)
                inventory_data_summary = sim.run_simulation()
                inventory_data_summary["service_level"] = service_level
                inventory_data_summary["agent"] = agent_info["name"]
                inventory_data_summary["environment"] = env_info["name"]
                inventory_data_summary["day"] = trial_number
                inventory_data_summaries.append(inventory_data_summary)

df_inventory_data_summaries = pd.DataFrame(inventory_data_summaries)
print(df_inventory_data_summaries.groupby(["service_level", "agent"]).agg({"write_offs": "mean", "fill_rate": "mean", "avg_service_level": "mean"})
)

plotter = simulation_plots.SimulationPlots(df_inventory_data_summaries)
plotter.run_dash_app()
