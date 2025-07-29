import ciw
import numpy as np

import montecarlo_simulator
import simulation_plots
from agent_environment import MonteCarloAgent, SafetyStockAgent, ForecastAgent, BaseAgent
from demand_environment import GammaPoisson, GammaGammaHighVariance, SingleGammaLowVariance, SpikingDemand
from demand_calculator import DemandCalculator
from config import SIM_DAYS, N_SIMULATIONS, HISTO_DAYS
np.random.seed(11)
ciw.random.seed(11)
print("Simulation of Agents over different Environments")

environment_configs = {
    0: {"name": "90/10 Gamma/Poisson", "class": GammaPoisson},
    1: {"name": "50/50 Gamma(mu=20)/Gamma(mu=200)", "class": GammaGammaHighVariance},
    2: {"name": "Spiking High Demand", "class": SpikingDemand},
    3: {"name": "Gamma", "class": SingleGammaLowVariance},
}

agent_configs = {
    0: {"name": "Historical Demand Agent", "class": BaseAgent},
    1: {"name": "Safety Stock Agent", "class": SafetyStockAgent},
    2: {"name": "Forecast Agent", "class": ForecastAgent},
    3: {"name": "Monte Carlo Agent", "class": MonteCarloAgent},
}

inventory_plot_data = []
sl_writeoff_plot_data = []

for env_info in environment_configs.values():
    env_class = env_info["class"]
    selected_environment = env_class(SIM_DAYS)
    selected_environment.generate_distribution()

    demand_calculator = DemandCalculator(SIM_DAYS)
    demand_calculator.set_environment(selected_environment)

    for agent_info in agent_configs.values():
        agent_class = agent_info["class"]

        print(f"\n--- Simulating Agent: {agent_info['name']} -> Running on Environment: {env_info['name']} ---")

        selected_agent = agent_class(demand_calculator, selected_environment)

        sim = montecarlo_simulator.MonteCarloSimulator(selected_agent, selected_environment)
        inventory_data_summary = sim.run_simulation(N_SIMULATIONS, SIM_DAYS)

        for i, result in enumerate(inventory_data_summary):
            inventory_level = result["inventory_level"]
            actual_demand = result["actual_demand"]
            for day, (inventory, demand) in enumerate(zip(inventory_level, actual_demand), start=HISTO_DAYS):
                inventory_plot_data.append(
                    {
                        "Agent": agent_info["name"],
                        "Environment": env_info["name"],
                        "Simulation Run": i + 1,
                        "Day": day,
                        "InventoryLevel": inventory,
                        "ActualDemand": demand,
                    }
                )

        for result in inventory_data_summary:
            sl_writeoff_plot_data.append(
                {
                    "Agent": agent_info["name"],
                    "Environment": env_info["name"],
                    "Write_Offs": result["write_offs"],
                    "Daily_Service_Level": result["avg_service_level"],
                    "Fill_Rate": result["fill_rate"]
                }
            )

        print(f"-- Simulation for {agent_info['name']} on {env_info['name']} Completed --")

plotter = simulation_plots.SimulationPlots(inventory_plot_data, sl_writeoff_plot_data)
plotter.run_dash_app()