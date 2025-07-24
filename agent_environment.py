import numpy as np
from abc import abstractmethod, ABC
from scipy.stats import norm
from config import LEAD_TIME, DEFAULT_SERVICE_LEVEL, MC_SIMS, HISTO_DAYS

class Agent(ABC):
    def __init__(self, daily_demand_distribution, environment):
        self.daily_demand_distribution = daily_demand_distribution
        self.demand_environment = environment

    @abstractmethod
    def compute_reorder_point(self, time_period) -> float:
        pass

    def get_forecasted_demand(self, time_period):
        demand_list = self.daily_demand_distribution.daily_demand_distribution
        end_time = time_period + LEAD_TIME
        future_actual_demands = [d.actual_demand for d in demand_list[time_period:end_time]]
        return future_actual_demands

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

        demand_mean = np.mean(historical_demand)
        demand_std = float(np.std(historical_demand, ddof=1)) # sample standard deviation

        safety_stock = norm.ppf(DEFAULT_SERVICE_LEVEL) * demand_std * np.sqrt(LEAD_TIME)
        return demand_mean * LEAD_TIME + safety_stock

class ForecastAgent(Agent):
    def __init__(self, daily_demand_distribution, environment):
        super().__init__(daily_demand_distribution, environment)

    def compute_reorder_point(self, time_period) -> float:
        forecasted_demand = self.get_forecasted_demand(time_period)

        forecast_demand_mean = np.mean(forecasted_demand)
        forecast_error = [forecast_demand_mean - demand for demand in forecasted_demand]
        forecast_error_std = np.std(forecast_error, ddof=1) # sample variance

        safety_stock = norm.ppf(DEFAULT_SERVICE_LEVEL) * forecast_error_std * np.sqrt(LEAD_TIME)
        return forecast_demand_mean * LEAD_TIME + safety_stock

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
