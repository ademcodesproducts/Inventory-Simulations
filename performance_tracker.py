class PerformanceTracker:

    def __init__(self, sim_days, histo_days):
        self.sim_days = sim_days
        self.histo_days = histo_days
        self.total_demand = 0
        self.total_fulfilled_demand = 0
        self.write_offs = 0
        self.stock_out_count = 0
        self.total_lost_sales = 0
        self.days_without_stockout = 0
        self.inventory_level = []
        self.actual_demand = []

    def daily_performance(self, demand_quantity, fulfilled_demand, daily_writeoff, inventory):
        self.total_demand += demand_quantity
        self.total_fulfilled_demand += fulfilled_demand
        self.write_offs += daily_writeoff
        self.total_lost_sales += max(demand_quantity - fulfilled_demand, 0)
        self.inventory_level.append(inventory)
        self.actual_demand.append(demand_quantity)

        if fulfilled_demand < demand_quantity:
            self.stock_out_count += 1
        else:
            self.days_without_stockout += 1

    def performance_summary(self):
        fill_rate = 1 - (self.total_demand - self.total_fulfilled_demand) / self.total_demand if self.total_demand > 0 else 0
        avg_service_level = self.days_without_stockout / (self.sim_days - self.histo_days) # change to cycle service level

        return {
            "total_demand": self.total_demand,
            "fulfilled_demand": self.total_fulfilled_demand,
            "fill_rate": fill_rate,
            "write_offs": self.write_offs,
            "stock_out_count": self.stock_out_count,
            "total_lost_sales": self.total_lost_sales,
            "avg_service_level": avg_service_level,
            "avg_inventory_level": sum(self.inventory_level) / len(self.inventory_level), # Average of inventory level list
            "inventory_level": self.inventory_level, # List
            "actual_demand": self.actual_demand # List
        }
