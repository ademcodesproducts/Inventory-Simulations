from config import SIM_DAYS, HISTO_DAYS


class PerformanceTracker:

    def __init__(self):
        self.total_demand = 0
        self.total_fulfilled_demand = 0
        self.fill_rate = 0
        self.write_offs = 0
        self.stock_out_count = 0
        self.total_lost_sales = 0
        self.days_without_stockout = 0

    # ADD INVENTORY KPI
    def daily_performance(self, demand_quantity, fulfilled_demand, daily_writeoff):
        self.total_demand += demand_quantity
        self.total_fulfilled_demand += fulfilled_demand
        self.fill_rate = 1 - (self.total_demand - self.total_fulfilled_demand ) / self.total_demand if self.total_demand > 0 else 0
        self.write_offs += daily_writeoff
        self.total_lost_sales += (demand_quantity - fulfilled_demand) if demand_quantity > fulfilled_demand else 0

        if fulfilled_demand < demand_quantity:
            self.stock_out_counter()
        else:
            self.days_without_stockout_counter()

    def stock_out_counter(self) -> int:
        self.stock_out_count += 1
        return self.stock_out_count

    def days_without_stockout_counter(self) -> int:
        self.days_without_stockout += 1
        return self.days_without_stockout

    def performance_summary(self):

        daily_service_level = self.days_without_stockout / (SIM_DAYS - HISTO_DAYS)

        return {
            "total_demand": self.total_demand,
            "fulfilled_demand": self.total_fulfilled_demand,
            "fill_rate": self.fill_rate,
            "write_offs": self.write_offs,
            "stock_out_count": self.stock_out_count,
            "total_lost_sales": self.total_lost_sales,
            "daily_service_level": daily_service_level
        }
