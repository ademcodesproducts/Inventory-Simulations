import ciw
from abc import abstractmethod, ABC
from typing import List, Tuple
from config import SHAPE_GAMMA_POISSON, LAMBDA_GAMMA_POISSON, SCALE_GAMMA_POISSON, SHAPE_GAMMA_GAMMA_LOW_MEAN, \
    SCALE_GAMMA_GAMMA_LOW_MEAN, SHAPE_GAMMA_GAMMA_HIGH_MEAN, SCALE_GAMMA_GAMMA_HIGH_MEAN, SHAPE_GAMMA_LOW_VAR, \
    SCALE_GAMMA_LOW_VAR, RATE_SPORADIC_HIGH, Seasonality
from demand_calculator import DailyDemandDistribution, DemandCalculator
    
class Environment(ABC):
    def __init__(self, sim_days: int):
        self.sim_days = sim_days
        self.demand_calculator = DemandCalculator(sim_days)
        self.demand_distribution = self.generate_distribution()

    @property
    def daily_demand_distribution(self) -> List[DailyDemandDistribution]:
        return self.demand_distribution

    @abstractmethod
    def create_distribution(self) -> ciw.dists.Distribution:
        pass

    @abstractmethod
    def get_distribution_params(self) -> Tuple[float, float, float]:
        pass

    @abstractmethod
    def get_weights(self) -> List[float]:
        pass

    def generate_distribution(self) -> List[DailyDemandDistribution]:
        daily_demand_distribution = []

        for day in range(self.sim_days):
            demand_distribution = self.create_distribution()
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
    def create_distribution(self) -> ciw.dists.Distribution:
        demand_distribution = ciw.dists.MixtureDistribution(
            [
                ciw.dists.Gamma(shape=SHAPE_GAMMA_POISSON, scale=SCALE_GAMMA_POISSON ),
                ciw.dists.Poisson(rate=LAMBDA_GAMMA_POISSON)
            ],
            [0.9, 0.1]
        )
        return demand_distribution

    def get_distribution_params(self) -> Tuple[float, float, float]:
        return SHAPE_GAMMA_POISSON, SCALE_GAMMA_POISSON, LAMBDA_GAMMA_POISSON

    def get_weights(self) -> List[float]:
        return [0.9, 0.1]

class GammaGammaHighVariance(Environment):

    def create_distribution(self) -> ciw.dists.Distribution:
        demand_distribution = ciw.dists.MixtureDistribution(
            [
                ciw.dists.Gamma(shape=SHAPE_GAMMA_GAMMA_LOW_MEAN, scale=SCALE_GAMMA_GAMMA_LOW_MEAN),
                ciw.dists.Gamma(shape=SHAPE_GAMMA_GAMMA_HIGH_MEAN, scale=SCALE_GAMMA_GAMMA_HIGH_MEAN)
            ],
            [0.5, 0.5]
        )
        return demand_distribution

    def get_distribution_params(self) -> Tuple[float, float, float]:
        return SHAPE_GAMMA_GAMMA_LOW_MEAN, SCALE_GAMMA_GAMMA_LOW_MEAN, SHAPE_GAMMA_GAMMA_HIGH_MEAN

    def get_weights(self) -> List[float]:
        return [0.5, 0.5]

class SpikingDemand(Environment):

    def create_distribution(self) -> str:
        demand_distribution = ciw.dists.MixtureDistribution(
            [
                ciw.dists.Deterministic(value=0),
                ciw.dists.Exponential(rate=RATE_SPORADIC_HIGH)
            ],
            [0.95, 0.05]
        )
        return demand_distribution

    def get_distribution_params(self) -> Tuple[float, float, float]:
        return 0.0, 0.0, RATE_SPORADIC_HIGH

    def get_weights(self) -> List[float]:
        return [0.95, 0.05]

class SingleGammaLowVariance(Environment):

    def create_distribution(self) -> ciw.dists.Distribution:
        demand_distribution = ciw.dists.Gamma(shape=SHAPE_GAMMA_LOW_VAR, scale=SCALE_GAMMA_LOW_VAR)
        return demand_distribution

    def get_distribution_params(self) -> Tuple[float, float, float]:
        return SHAPE_GAMMA_LOW_VAR, SCALE_GAMMA_LOW_VAR, 0.0

    def get_weights(self) -> List[float]:
        return [1.0, 0.0]
