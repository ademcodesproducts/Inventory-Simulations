from abc import ABC, abstractmethod
import numpy as np
from scipy.stats import norm
from config import HISTO_DAYS, LEAD_TIME, MC_SIMS, DEFAULT_SERVICE_LEVEL
from safety_stock_experimentations.demand_distribution import DailyDemandDistribution


class Agent(ABC):
    def __init__(self, daily_demand_distributions: list[DailyDemandDistribution], service_level: float = DEFAULT_SERVICE_LEVEL):
        self._daily_demand_distributions = daily_demand_distributions
        self.service_level = service_level

    @abstractmethod
    def compute_reorder_point(self, time_period) -> float:
        pass

    def get_historical_demand(self, time_period):
        start_time = time_period - HISTO_DAYS
        return [
            d.realised_demand
            for d in self._daily_demand_distributions[start_time:time_period]
        ]


class BaseAgent(Agent):
    def compute_reorder_point(self, time_period):
        historical_demand = self.get_historical_demand(time_period)
        demand_mean = np.mean(historical_demand)
        return demand_mean * LEAD_TIME


class SafetyStockAgent(Agent):
    def compute_reorder_point(self, time_period) -> float:
        historical_demand = self.get_historical_demand(time_period)

        demand_mean = np.mean(historical_demand)
        demand_std = float(
            np.std(historical_demand, ddof=1)
        )  # sample standard deviation

        safety_stock = (
            norm.ppf(self.service_level) * demand_std * np.sqrt(LEAD_TIME)
        )
        return demand_mean * LEAD_TIME + safety_stock


class ForecastAgent(Agent):
    def __init__(self, daily_demand_distribution, service_level):
        super().__init__(daily_demand_distribution, service_level)

    def compute_reorder_point(self, time_period) -> float:
        forecast_demand_sum = 0

        max_index = len(self._daily_demand_distributions) - 1

        for t in range(time_period + 1, time_period + 1 + LEAD_TIME):
            index = min(t, max_index)
            forecast_demand_sum += self._daily_demand_distributions[
                index
            ].mean_demand_distribution

        start_time = time_period - HISTO_DAYS
        forecast_errors = [
            self._daily_demand_distributions[
                min(day, max_index)
            ].mean_demand_distribution
            - self._daily_demand_distributions[min(day, max_index)].realised_demand
            for day in range(start_time, time_period)
        ]

        forecast_error_std = np.std(forecast_errors, ddof=1)

        safety_stock = (
            norm.ppf(self.service_level)
            * forecast_error_std
            * np.sqrt(LEAD_TIME)
        )

        return forecast_demand_sum + safety_stock


class MonteCarloAgent(Agent):
    def __init__(self, daily_demand_distribution, service_level):
        super().__init__(daily_demand_distribution, service_level)

    def compute_reorder_point(self, time_period) -> float:
        samples = self._sample_lead_time_demand(
            time_period=time_period,
            daily_demand_distribution=self._daily_demand_distributions,
            mc_sims=MC_SIMS,
        )
        return float(np.quantile(samples, self.service_level))

    def _sample_lead_time_demand(self, time_period, daily_demand_distribution, mc_sims):
        samples = []
        max_index = len(daily_demand_distribution) - 1
        for i in range(mc_sims):
            total_demand = 0
            for j in range(1, LEAD_TIME + 1):
                index = min(time_period + j, max_index)
                total_demand += daily_demand_distribution[
                    index
                ].demand_distribution.sample()
            samples.append(total_demand)
        return samples
