from abc import abstractmethod, ABC
from typing import Tuple
import numpy as np
from scipy.stats import norm
from config import LEAD_TIME, DEFAULT_SERVICE_LEVEL, MC_SIMS, HISTO_DAYS
from demand_calculator import DemandCalculator

class Agent(ABC):
    def __init__(self, daily_demand_distribution, environment):
        self.daily_demand_distribution = daily_demand_distribution
        self.demand_environment = environment

    @abstractmethod
    def compute_reorder_point(self, time_period) -> float:
        pass

    def get_demand_stats(self) -> Tuple[float, float]:
        shape, scale, rate = self.demand_environment.get_distribution_params()
        weights = self.demand_environment.get_weights()
        return DemandCalculator.get_demand_stats(shape, scale, rate, weights)

    def get_historical_demand(self, time_period):
        start_time = time_period - HISTO_DAYS
        demand_list = self.daily_demand_distribution.daily_demand_distribution
        return [d.actual_demand for d in demand_list[start_time:time_period]]

class BaseAgent(Agent):

    def compute_reorder_point(self, time_period):
        historical_demand = self.get_historical_demand(time_period)
        demand_mean = np.mean(historical_demand)
        return demand_mean * LEAD_TIME

class SafetyStockAgent(Agent):

    def compute_reorder_point(self, time_period) -> float:
        historical_demand = self.get_historical_demand(time_period)
dd
        demand_mean = np.mean(historical_demand)
        demand_std = np.std(historical_demand, ddof=1)  # sample standard deviation

        safety_stock = norm.ppf(DEFAULT_SERVICE_LEVEL) * demand_std * np.sqrt(LEAD_TIME)
        return demand_mean * LEAD_TIME + safety_stock

class ForecastAgent(Agent):
    def __init__(self, daily_demand_distribution, environment):
        super().__init__(daily_demand_distribution, environment)

    def compute_reorder_point(self, time_period) -> float:
        shape, scale, rate = self.demand_environment.get_distribution_params()
        weights = self.demand_environment.get_weights()

        demand_mean, demand_std = DemandCalculator.get_demand_stats(shape, scale, rate, weights)

        safety_stock = norm.ppf(DEFAULT_SERVICE_LEVEL) * demand_std * np.sqrt(LEAD_TIME)
        return demand_mean * LEAD_TIME + safety_stock

class MonteCarloAgent(Agent):
    def __init__(self, daily_demand_distribution, environment):
        super().__init__(daily_demand_distribution, environment)
        self.q = DEFAULT_SERVICE_LEVEL

    def compute_reorder_point(self, time_period) -> float:
        samples = self.daily_demand_distribution.sample_lead_time_demand(
            time_period=time_period,
            daily_demand_distribution=self.daily_demand_distribution.daily_demand_distribution,
            mc_sims=MC_SIMS
        )
        return float(np.quantile(samples, self.q))
