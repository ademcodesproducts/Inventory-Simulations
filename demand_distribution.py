from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime as dt

import ciw
import numpy as np

from safety_stock_experimentations.config import (
    SIM_DAYS,
    SIMULATION_START_DATE,
    N_SAMPLES,
)
from safety_stock_experimentations.demand_distribution_parameters import (
    GammaParameterRange,
    PoissonParameterRange,
    GammaHighVarianceParameterRange,
)


@dataclass
class DailyDemandDistribution:
    time_step: int
    realised_demand: int
    demand_distribution: ciw.dists.Distribution
    mean_demand_distribution: float


class DailyDemandDistributionBuilder(ABC):
    def execute(self) -> list[DailyDemandDistribution]:
        daily_demand_distributions = []
        for time_step in range(SIM_DAYS):
            distribution = self._get_daily_demand_distribution(time_step)
            distribution_mean = float(
                np.mean([distribution.sample() for _ in range(N_SAMPLES)])
            )
            daily_demand_distributions.append(
                DailyDemandDistribution(
                    time_step=time_step,
                    realised_demand=int(distribution.sample()),
                    demand_distribution=distribution,
                    mean_demand_distribution=distribution_mean,
                )
            )
        return daily_demand_distributions

    @abstractmethod
    def _get_daily_demand_distribution(self, time_step: int) -> ciw.dists.Distribution:
        pass

    @staticmethod
    def _get_daily_seasonality_multiplier(time_step: int) -> float:
        current_date = SIMULATION_START_DATE + dt.timedelta(days=time_step)

        month_multipliers = {
            12: 1.10, # 12: 1.10,
            11: 1.20, # 11: 1.20,
            10: 1.30, # 10: 1.30,
            9: 1.40, # 9: 1.40,
            8: 1.50, # 8: 1.50,
            7: 1.50, # 7: 1.50,
            6: 1.30, # 6: 1.30,
            5: 1.20, # 5: 1.20,
            4: 1.10, # 4: 1.10,
        }
        month_multiplier = month_multipliers.get(current_date.month, 1.0)

        weekday_multipliers = {
            5: 1.50,  # Saturday
            0: 1.20,  # Monday
            4: 1.20,  # Friday
        }
        weekday_multiplier = weekday_multipliers.get(current_date.weekday(), 1.0)

        return month_multiplier * weekday_multiplier


class GammaPoisson(DailyDemandDistributionBuilder):
    def __init__(
        self,
        gamma_parameter_range: GammaParameterRange = GammaParameterRange(),
        poisson_parameter_range: PoissonParameterRange = PoissonParameterRange(),
    ):
        super().__init__()
        self._gamma_parameter_range = gamma_parameter_range
        self._poisson_parameter_range = poisson_parameter_range

    def _get_daily_demand_distribution(self, time_step: int) -> ciw.dists.Distribution:
        seasonality_multiplier = self._get_daily_seasonality_multiplier(time_step)
        return ciw.dists.MixtureDistribution(
            [
                ciw.dists.Gamma(
                    shape=self._gamma_parameter_range.sample_shape(),
                    scale=self._gamma_parameter_range.sample_scale() * seasonality_multiplier,
                ),
                ciw.dists.Poisson(rate=self._poisson_parameter_range.sample()),
            ],
            [0.9, 0.1],
        )


class GammaGammaHighVariance(DailyDemandDistributionBuilder):
    def __init__(
        self,
        gamma_parameter_range: GammaHighVarianceParameterRange = GammaHighVarianceParameterRange(),
    ):
        super().__init__()
        self._gamma_parameter_range = gamma_parameter_range

    def _get_daily_demand_distribution(self, time_step: int) -> ciw.dists.Distribution:
        seasonality_multiplier = self._get_daily_seasonality_multiplier(time_step)
        return ciw.dists.MixtureDistribution(
            [
                ciw.dists.Gamma(
                    shape=self._gamma_parameter_range.sample_shape_low(),
                    scale=self._gamma_parameter_range.sample_scale_low()  * seasonality_multiplier,
                ),
                ciw.dists.Gamma(
                    shape=self._gamma_parameter_range.sample_shape_high(),
                    scale=self._gamma_parameter_range.sample_scale_high()  * seasonality_multiplier,
                ),
            ],
            [0.5, 0.5],
        )


class SingleGammaLowVariance(DailyDemandDistributionBuilder):
    def __init__(
        self,
        gamma_parameter_range: GammaParameterRange = GammaParameterRange(),
    ):
        super().__init__()
        self._gamma_parameter_range = gamma_parameter_range

    def _get_daily_demand_distribution(self, time_step: int) -> ciw.dists.Distribution:
        seasonality_multiplier = self._get_daily_seasonality_multiplier(time_step)
        return ciw.dists.Gamma(
            shape=self._gamma_parameter_range.sample_shape(),
            scale=self._gamma_parameter_range.sample_scale() * seasonality_multiplier,
        )
