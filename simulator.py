import pandas as pd
from config import HISTO_DAYS, LEAD_TIME, N_SIMULATIONS, SIM_DAYS
from inventory_manager import InventoryManager
from order_processor import OrderProcessor
from performance_tracker import PerformanceTracker


class Simulator:
    def __init__(self, agent, environment):
        self.agent = agent
        self.environment = environment

    def run_simulation(self):
        order_processor = OrderProcessor()
        performance_tracker = PerformanceTracker()
        inventory_manager = InventoryManager(
            order_processor=order_processor, agent=self.agent
        )

        for day in range(HISTO_DAYS, SIM_DAYS):
            demand_quantity = self.environment[day].realised_demand

            inventory_manager.process_deliveries(day)
            fulfilled_demand = min(demand_quantity, inventory_manager.inventory)
            inventory_manager.inventory_update(fulfilled_demand)
            daily_writeoff = inventory_manager.apply_writeoff()
            inventory_manager.reorder(day)

            if not ((day < HISTO_DAYS + LEAD_TIME + 2) | (day > SIM_DAYS - LEAD_TIME)):
                performance_tracker.daily_performance(
                    day=day,
                    demand_quantity=demand_quantity,
                    fulfilled_demand=fulfilled_demand,
                    daily_writeoff=daily_writeoff,
                    inventory=inventory_manager.inventory,
                    order_processor=order_processor,
                )
            # TODO: How to handle cases where it's very unlikely that the sales are realised at T+1/T+2. Idea: Order at most the 95% quantile of the sales for T+3

        return performance_tracker.performance_summary()
