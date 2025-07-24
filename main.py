import montecarlo_simulator
from agent_environment import MonteCarloAgent, SafetyStockAgent, ForecastAgent, BaseAgent
from demand_environment import GammaPoisson, GammaGammaHighVariance, SingleGammaLowVariance, SpikingDemand
from demand_calculator import DemandCalculator
from config import SIM_DAYS, N_SIMULATIONS
import ciw
ciw.seed(11)

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

for agent_info in agent_configs.values():
    for env_info in environment_configs.values():
        agent_class = agent_info["class"]
        env_class = env_info["class"]
        print(f"\n--- Simulating Agent: {agent_info['name']} -> Running on Environment: {env_info['name']} ---")

        selected_environment = env_class(SIM_DAYS)

        demand_calculator = DemandCalculator(SIM_DAYS)
        demand_calculator.set_environment(selected_environment)
        daily_demand_distribution = demand_calculator

        selected_agent = agent_class(daily_demand_distribution, selected_environment)

        sim = montecarlo_simulator.MonteCarloSimulator(selected_agent, selected_environment)
        sim.run_simulation(N_SIMULATIONS, SIM_DAYS)

        print(f"-- Simulation for {agent_info['name']} on {env_info['name']} Completed --")

