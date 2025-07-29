import pandas as pd
from config import LEAD_TIME, HISTO_DAYS
from order_processor import OrderProcessor
from inventory_manager import InventoryManager
from performance_tracker import PerformanceTracker

class MonteCarloSimulator():
    def __init__(self, agent, environment):
        self.agent = agent
        self.environment = environment

    def run_simulation(self, N_SIMULATIONS, SIM_DAYS):
        all_simulation_results = []

        for sim in range(N_SIMULATIONS):
            time_period = 0
            order_processor = OrderProcessor()
            performance_tracker = PerformanceTracker(SIM_DAYS, HISTO_DAYS)

            inventory_manager = InventoryManager(
                order_processor=order_processor,
                agent=self.agent
            )

            for day in range(HISTO_DAYS):
                _ = self.agent.daily_demand_distribution.daily_demand_distribution[day].actual_demand

            for day in range(HISTO_DAYS, SIM_DAYS):
                demand_quantity = self.agent.daily_demand_distribution.daily_demand_distribution[day].actual_demand

                base_inventory = inventory_manager.inventory

                inventory_manager.inventory_update(demand_quantity)

                if day < SIM_DAYS - LEAD_TIME:
                    inventory_manager.reorder(day)

                inventory_manager.process_deliveries(day)

                fulfilled_demand = min(demand_quantity, base_inventory) # demand that doesnt exceed inventory
                daily_writeoff = inventory_manager.apply_writeoff(day)
                inventory = inventory_manager.get_inventory()

                performance_tracker.daily_performance(
                    demand_quantity=demand_quantity,
                    fulfilled_demand=fulfilled_demand,
                    daily_writeoff=daily_writeoff,
                    inventory=inventory,
                )

                time_period += 1

            print(f"\n Simulation {sim + 1}")
            print("-" * 30)
            sim_summary = performance_tracker.performance_summary()

            for key, value in sim_summary.items():
                print(f"{key.title()}: {value}")

            all_simulation_results.append(sim_summary)

        self.generate_overall_report(all_simulation_results)
        return all_simulation_results

    def generate_overall_report(self, results):
        df = pd.DataFrame(results)
        df_selected = df.drop(columns=["inventory_level", "actual_demand"])
        summary_stats = df_selected.agg(['mean']).transpose()
        summary_stats.columns = ['Mean']
        print("Cummulative Simulation Results")
        print("---------------------------------------------")
        print(summary_stats.to_string(float_format="%.6f"))
