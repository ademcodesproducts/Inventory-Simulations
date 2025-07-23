# Simulation constraints
import datetime
import numpy as np
np.random.seed(42)

SIM_DAYS = 730
HISTO_DAYS = 365
N_SIMULATIONS = 100
MC_SIMS = 1000

# Replenishment constraints & constants
WRITE_OFF_RATE = 0.01

# Stock constraints
LEAD_TIME = 3
BASE_STOCK = 0
DEFAULT_SERVICE_LEVEL = 0.95

# Demand constraints
SHAPE_GAMMA_POISSON = np.random.uniform(6, 8) # 7
SCALE_GAMMA_POISSON = np.random.uniform(14, 18) # 16
LAMBDA_GAMMA_POISSON = np.random.uniform(75, 85) # 80

SHAPE_GAMMA_GAMMA_LOW_MEAN = np.random.uniform(6, 8) # 7
SCALE_GAMMA_GAMMA_LOW_MEAN = np.random.uniform(2, 4) # 3
SHAPE_GAMMA_GAMMA_HIGH_MEAN = np.random.uniform(6, 8) # 7
SCALE_GAMMA_GAMMA_HIGH_MEAN = np.random.uniform(28, 30) # 29

SHAPE_GAMMA_LOW_VAR = np.random.uniform(6, 8) # 7
SCALE_GAMMA_LOW_VAR = np.random.uniform(14, 18) # 16

RATE_SPORADIC_HIGH = np.random.uniform(0.005, 0.1)  # 0.05

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