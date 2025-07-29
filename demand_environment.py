import datetime
import ciw
from abc import abstractmethod, ABC
from typing import List
from config import (
    sample_gamma_poisson_params,
    sample_gamma_gamma_params,
    sample_single_gamma_params,
    sample_spiking_params,
)
from demand_calculator import DailyDemandDistribution, DemandCalculator
from config import Seasonality


class Environment(ABC):
    def __init__(self, sim_days: int):
        self.sim_days = sim_days
        self.demand_calculator = DemandCalculator(sim_days)
        self.start_date = datetime.date(2023, 1, 1)
        self.params = None
        self.demand_distribution = []

    @property
    def daily_demand_distribution(self) -> List[DailyDemandDistribution]:
        return self.demand_distribution

    @abstractmethod
    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:
        pass

    def generate_distribution(self) -> List[DailyDemandDistribution]:

        daily_demand_distribution = []
        for day in range(self.sim_days):
            dist = self.create_distribution(day)
            actual_demand = int(dist.sample())
            daily_demand_distribution.append(
                DailyDemandDistribution(
                    day=day,
                    actual_demand=actual_demand,
                    forecast_distribution=dist
                )
            )
        self.demand_distribution = daily_demand_distribution
        return daily_demand_distribution

class GammaPoisson(Seasonality, Environment):
    def __init__(self, sim_days: int):
        super().__init__(sim_days)
        self.params = sample_gamma_poisson_params()

    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:
        demand_multiplier = self.get_daily_seasonality(time_period)
        shape = self.params["shape"]
        scale = self.params["scale"] * demand_multiplier
        lambda_ = self.params["lambda_"] * demand_multiplier

        return ciw.dists.MixtureDistribution(
            [
                ciw.dists.Gamma(shape=shape, scale=scale),
                ciw.dists.Poisson(rate=lambda_)
            ],
            [0.9, 0.1]
        )


class GammaGammaHighVariance(Seasonality, Environment):
    def __init__(self, sim_days: int):
        super().__init__(sim_days)
        self.params = sample_gamma_gamma_params()

    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:
        demand_multiplier = self.get_daily_seasonality(time_period)
        scale_low = self.params["low_scale"] * demand_multiplier
        scale_high = self.params["high_scale"] * demand_multiplier

        return ciw.dists.MixtureDistribution(
            [
                ciw.dists.Gamma(shape=self.params["low_shape"], scale=scale_low),
                ciw.dists.Gamma(shape=self.params["high_shape"], scale=scale_high)
            ],
            [0.5, 0.5]
        )


class SpikingDemand(Seasonality, Environment):
    def __init__(self, sim_days: int):
        super().__init__(sim_days)
        self.params = sample_spiking_params()

    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:
        demand_multiplier = self.get_daily_seasonality(time_period)
        spike_rate = self.params["rate_sporadic_high"] * demand_multiplier

        return ciw.dists.MixtureDistribution(
            [
                ciw.dists.Deterministic(value=0),
                ciw.dists.Deterministic(value=spike_rate)
            ],
            [0.95, 0.05]
        )


class SingleGammaLowVariance(Seasonality, Environment):
    def __init__(self, sim_days: int):
        super().__init__(sim_days)
        self.params = sample_single_gamma_params()

    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:
        demand_multiplier = self.get_daily_seasonality(time_period)
        shape = self.params["shape"]
        scale = self.params["scale"] * demand_multiplier

        return ciw.dists.Gamma(shape=shape, scale=scale)
