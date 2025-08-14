from dataclasses import dataclass
import numpy as np


@dataclass
class PoissonParameterRange:
    rate_min: float = 75
    rate_max: float = 85

    def sample(self) -> float:
        return np.random.uniform(self.rate_min, self.rate_max)


@dataclass
class GammaParameterRange:
    shape_min: float = 6
    shape_max: float = 8
    scale_min: float = 14
    scale_max: float = 18

    def sample_shape(self) -> float:
        return np.random.uniform(self.shape_min, self.shape_max)

    def sample_scale(self) -> float:
        return np.random.uniform(self.scale_min, self.scale_max)


@dataclass
class GammaHighVarianceParameterRange:
    shape_min_low: float = 6
    shape_max_low: float = 8
    scale_min_low: float = 2
    scale_max_low: float = 4

    shape_min_high: float = 6
    shape_max_high: float = 8
    scale_min_high: float = 28
    scale_max_high: float = 30

    def sample_shape_low(self) -> float:
        return np.random.uniform(self.shape_min_low, self.shape_max_low)

    def sample_scale_low(self) -> float:
        return np.random.uniform(self.scale_min_low, self.scale_max_low)

    def sample_shape_high(self) -> float:
        return np.random.uniform(self.shape_min_high, self.shape_max_high)

    def sample_scale_high(self) -> float:
        return np.random.uniform(self.scale_min_high, self.scale_max_high)
