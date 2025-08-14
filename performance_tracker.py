import numpy as np


class PerformanceTracker:

    def __init__(self):
        self.total_demand = 0
        self.total_fulfilled_demand = 0
        self.write_offs = 0
        self.stock_out_count = 0
        self.total_lost_sales = 0
        self.days_without_stockout = 0
        self.daily_performance_metrics = []

    def daily_performance(
        self, day, demand_quantity, fulfilled_demand, daily_writeoff, inventory, order_processor
    ):
        self.total_fulfilled_demand += fulfilled_demand
        self.write_offs += daily_writeoff
        self.total_lost_sales += max(demand_quantity - fulfilled_demand, 0)
        self.total_demand += demand_quantity
        is_stockout_day = fulfilled_demand < demand_quantity

        if is_stockout_day:
            self.stock_out_count += 1
        else:
            self.days_without_stockout += 1

        self.daily_performance_metrics.append(
            {
                "day": day,
                "demand": demand_quantity,
                "fulfilled_demand": fulfilled_demand,
                "write_offs": daily_writeoff,
                "inventory": inventory,
                "is_stockout_day": is_stockout_day,
                "order_t+1": order_processor.get_order_at_date(day + 1),
                "order_t+2": order_processor.get_order_at_date(day + 2),
                "order_t+3": order_processor.get_order_at_date(day + 3),
            }
        )

    def performance_summary(self):
        fill_rate = (
            1 - (self.total_demand - self.total_fulfilled_demand) / self.total_demand
            if self.total_demand > 0
            else 0
        )
        avg_service_level = self.days_without_stockout / (
            len(self.daily_performance_metrics)
        )

        return {
            "total_demand": self.total_demand,
            "fulfilled_demand": self.total_fulfilled_demand,
            "fill_rate": fill_rate,
            "write_offs": self.write_offs,
            "stock_out_count": self.stock_out_count,
            "total_lost_sales": self.total_lost_sales,
            "avg_service_level": avg_service_level,
            "avg_inventory_level": np.mean(
                [
                    performance_metrics_for_given_day["inventory"]
                    for performance_metrics_for_given_day in self.daily_performance_metrics
                ]
            ),
            "daily_performance_metrics": self.daily_performance_metrics,
        }
