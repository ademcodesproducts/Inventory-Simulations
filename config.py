import datetime
import numpy as np

# Simulation constraints

SIM_DAYS = 730
HISTO_DAYS = 365
N_SIMULATIONS = 20
MC_SIMS = 100

# Replenishment constants
WRITE_OFF_RATE = 0.01

# Stock constraints
LEAD_TIME = 3
BASE_STOCK = 0
DEFAULT_SERVICE_LEVEL = 0.95

def sample_gamma_poisson_params():
    return {
        "shape": np.random.uniform(6, 8),
        "scale": np.random.uniform(14, 18),
        "lambda_": np.random.uniform(75, 85),
    }

def sample_gamma_gamma_params():
    return {
        "low_shape": np.random.uniform(6, 8),
        "low_scale": np.random.uniform(2, 4),
        "high_shape": np.random.uniform(6, 8),
        "high_scale": np.random.uniform(28, 30),
    }

def sample_single_gamma_params():
    return {
        "shape": np.random.uniform(6, 8),
        "scale": np.random.uniform(14, 18),
    }

def sample_spiking_params():
    return {
        "rate_sporadic_high": np.random.uniform(180, 220),
    }

class Seasonality:
    def __init__(self, sim_days):
        self.sim_days = sim_days
        self.start_date = datetime.date(2023, 1, 1)

    def get_daily_seasonality(self, time_period) -> float:
        current_date = self.start_date + datetime.timedelta(days=time_period)
        month = current_date.month
        day_of_week = time_period % 7

        month_multipliers = {
            8: 1.50,
            7: 1.40,
            6: 1.30,
            5: 1.20,
            4: 1.10
        }
        month_multiplier = month_multipliers.get(month, 1.0) # Retrieve multiplier for current_date.month

        weekday_multipliers = {
            5: 1.50,  # Saturday
            0: 1.20,  # Monday
            4: 1.20,  # Friday
        }
        weekday_multiplier = weekday_multipliers.get(day_of_week, 1.0) # Retrieves the multiplier for current_date.weekday

        return month_multiplier * weekday_multiplier