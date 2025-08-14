import datetime as dt

# Simulation constraints
SIMULATION_START_DATE = dt.date(2023, 1, 1)
SIM_DAYS = 730
HISTO_DAYS = 365
N_SIMULATIONS = 100  # 100
MC_SIMS = 1000  # 1000
N_SAMPLES = 100  # 100

# Replenishment constants
WRITE_OFF_RATE = 0.01

# Stock constraints
LEAD_TIME = 3
BASE_STOCK = 0
DEFAULT_SERVICE_LEVEL = 0.95
