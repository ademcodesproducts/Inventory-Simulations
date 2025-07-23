import numpy as np
import ciw.dists
from dataclasses import dataclass
from typing import Tuple
from config import LEAD_TIME

np.random.seed(42)

@dataclass
class DailyDemandDistribution:
    day: int
    actual_demand: int
    forecast_distribution: ciw.dists.Distribution

class DemandCalculator:
    def __init__(self, sim_days: int):
        self.sim_days = sim_days
        self.daily_demand_distribution = []

    def set_environment(self, environment):
        self.environment = environment
        self.daily_demand_distribution = self.environment.generate_distribution()

    def get_daily_demand(self, time_period: int) -> int:
        return self.daily_demand_distribution[time_period].actual_demand

    def sample_lead_time_demand(self, time_period, daily_demand_distribution, mc_sims):
        samples = []
        for i in range(mc_sims):
            total_demand = 0
            for j in range(1, LEAD_TIME + 1):
                total_demand += daily_demand_distribution[time_period + j].forecast_distribution.sample()
            samples.append(total_demand)
        return samples

    @staticmethod
    def get_demand_stats(shape: Tuple[float, float], scale: Tuple[float, float], rate: float, weights: list[float]) -> Tuple[float, float]:
        mean_gamma_base = shape[0] * scale[0]
        mean_gamma_ext = shape[1] * scale[1]
        mean_poisson = rate

        var_gamma_base = shape[0] * scale[0] ** 2
        var_gamma_ext = shape[1] * scale[1] ** 2
        var_poisson = rate

        mixture_mean = weights[0] * mean_gamma_base + weights[1] * mean_gamma_ext + weights[1] * mean_poisson

        mixture_var = (
                weights[0] * (var_gamma_base + (mean_gamma_base - mixture_mean) ** 2) +
                weights[1] * (var_gamma_ext + (mean_gamma_ext - mixture_mean) ** 2) +
                weights[1] * (var_poisson + (mean_poisson - mixture_mean) ** 2)
        )
        mixture_std = float(np.sqrt(mixture_var))

        return mixture_mean, mixture_std

    """@staticmethod
    def get_demand_stats(distribution: ciw.dists.Distribution) -> Tuple[float, float]:
        total_mean = 0.0
        total_variance = 0.0

        components = []
        weights = []

        if isinstance(distribution, ciw.dists.MixtureDistribution):
            components = distribution.distributions
            weights = distribution.weights
        else:
            # Handle single distributions as a mixture with one component and weight 1.0
            components = [distribution]
            weights = [1.0]

        # Calculate mean and variance for each component
        component_stats = [] # List of (mean_i, var_i) for each component
        for comp in components:
            if isinstance(comp, ciw.dists.Gamma):
                mean_c = comp.shape * comp.scale
                var_c = comp.shape * (comp.scale ** 2)
            elif isinstance(comp, ciw.dists.Poisson):
                mean_c = comp.rate
                var_c = comp.rate
            elif isinstance(comp, ciw.dists.Deterministic):
                mean_c = float(comp.value)
                var_c = 0.0
            elif isinstance(comp, ciw.dists.Exponential):
                if comp.rate == 0:
                    mean_c = float('inf') # Or handle as a specific case if infinite mean is not desired
                    var_c = float('inf')
                else:
                    mean_c = 1.0 / comp.rate
                    var_c = 1.0 / (comp.rate ** 2)
            else:
                print(f"Warning: Unsupported CIW distribution type encountered in get_demand_stats: {type(comp)}. Estimating from samples.")
                # Fallback: estimate mean/variance from samples if analytical formula is unknown
                samples = [comp.sample() for _ in range(1000)]
                mean_c = np.mean(samples)
                var_c = np.var(samples)

            component_stats.append((mean_c, var_c))

        # Calculate overall mixture mean
        for i in range(len(components)):
            total_mean += weights[i] * component_stats[i][0]

        # Calculate overall mixture variance using law of total variance
        for i in range(len(components)):
            mean_i, var_i = component_stats[i]
            total_variance += weights[i] * (var_i + (mean_i - total_mean) ** 2)

        mixture_std = float(np.sqrt(total_variance))

        return total_mean, mixture_std
        """

