import datetime
import ciw
from abc import abstractmethod, ABC
from typing import List, Tuple
from config import SHAPE_GAMMA_POISSON, LAMBDA_GAMMA_POISSON, SCALE_GAMMA_POISSON, SHAPE_GAMMA_GAMMA_LOW_MEAN, \
    SCALE_GAMMA_GAMMA_LOW_MEAN, SHAPE_GAMMA_GAMMA_HIGH_MEAN, SCALE_GAMMA_GAMMA_HIGH_MEAN, SHAPE_GAMMA_LOW_VAR, \
    SCALE_GAMMA_LOW_VAR, RATE_SPORADIC_HIGH, Seasonality, SIM_DAYS
from demand_calculator import DailyDemandDistribution, DemandCalculator


class Environment(ABC):
    def __init__(self, sim_days: int):
        self.sim_days = sim_days
        self.demand_calculator = DemandCalculator(sim_days)
        self.start_date = datetime.date(2023, 1, 1)
        self.demand_distribution = self.generate_distribution()

    @property
    def daily_demand_distribution(self) -> List[DailyDemandDistribution]:
        return self.demand_distribution

    @abstractmethod
    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:
        pass

    def generate_distribution(self) -> List[DailyDemandDistribution]:
        daily_demand_distribution = []

        for day in range(SIM_DAYS):
            demand_distribution = self.create_distribution(day)
            actual_demand = int(demand_distribution.sample())

            daily_demand_distribution.append(
                DailyDemandDistribution(
                    day=day,
                    actual_demand=actual_demand,
                    forecast_distribution=demand_distribution
                )
            )
        return daily_demand_distribution

class GammaPoisson(Seasonality, Environment):
    def __init__(self, sim_days: int):
        super().__init__(sim_days)

    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:

        demand_multiplier = self.get_daily_seasonality(time_period)
        seasonal_scale = SCALE_GAMMA_POISSON * demand_multiplier
        seasonal_rate = LAMBDA_GAMMA_POISSON * demand_multiplier

        demand_distribution = ciw.dists.MixtureDistribution(
            [
                ciw.dists.Gamma(shape=SHAPE_GAMMA_POISSON, scale=seasonal_scale),
                ciw.dists.Poisson(rate=seasonal_rate)
            ],
            [0.9, 0.1]
        )
        return demand_distribution

class GammaGammaHighVariance(Seasonality, Environment):
    def __init__(self, sim_days: int):
        super().__init__(sim_days)

    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:

        demand_multiplier = self.get_daily_seasonality(time_period)
        seasonal_scale_low = SCALE_GAMMA_GAMMA_LOW_MEAN * demand_multiplier
        seasonal_scale_high = SCALE_GAMMA_GAMMA_HIGH_MEAN * demand_multiplier

        demand_distribution = ciw.dists.MixtureDistribution(
            [
                ciw.dists.Gamma(shape=SHAPE_GAMMA_GAMMA_LOW_MEAN, scale=seasonal_scale_low),
                ciw.dists.Gamma(shape=SHAPE_GAMMA_GAMMA_HIGH_MEAN, scale=seasonal_scale_high)
            ],
            [0.5, 0.5]
        )
        return demand_distribution

class SpikingDemand(Seasonality, Environment):
    def __init__(self, sim_days: int):
        super().__init__(sim_days)

    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:

        demand_multiplier = self.get_daily_seasonality(time_period)
        seasonal_sporadic_high = RATE_SPORADIC_HIGH * demand_multiplier

        demand_distribution = ciw.dists.MixtureDistribution(
            [
                ciw.dists.Deterministic(value=0),
                ciw.dists.Exponential(rate=seasonal_sporadic_high)
            ],
            [0.95, 0.05]
        )
        return demand_distribution

class SingleGammaLowVariance(Seasonality, Environment):
    def __init__(self, sim_days: int):
        super().__init__(sim_days)

    def create_distribution(self, time_period: int) -> ciw.dists.Distribution:

        demand_multiplier = self.get_daily_seasonality(time_period)
        seasonal_gamma_scale = SCALE_GAMMA_LOW_VAR * demand_multiplier
        demand_distribution = ciw.dists.Gamma(shape=SHAPE_GAMMA_LOW_VAR, scale=seasonal_gamma_scale)
        return demand_distribution
