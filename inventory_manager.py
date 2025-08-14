from safety_stock_experimentations.config import BASE_STOCK, WRITE_OFF_RATE


class InventoryManager:
    def __init__(self, order_processor, agent):
        self.inventory = BASE_STOCK
        self.order_processor = order_processor
        self.total_write_off_quantity = 0
        self.agent = agent

    def reorder(self, time_period):
        reorder_point = self.agent.compute_reorder_point(time_period)
        orders_in_delivery = self.order_processor.get_incoming_orders(time_period)
        expected_inventory = self.inventory + orders_in_delivery

        if expected_inventory <= reorder_point:
            # ordered quantity is reorder point minus current inventory and orders in delivery
            order_quantity = reorder_point - expected_inventory
            self.order_processor.place_order(time_period, order_quantity)

    def inventory_update(self, demand_quantity):
        self.inventory -= demand_quantity

    def apply_writeoff(self):
        write_off_quantity = self.inventory * WRITE_OFF_RATE
        self.inventory -= write_off_quantity
        # TODO: Nothing to do, one could just thing about making the inventory change parametrizable (either it happens or not)
        self.total_write_off_quantity += write_off_quantity
        return write_off_quantity

    def process_deliveries(self, time_period):
        processed_delivery = self.order_processor.manage_order(time_period)
        self.inventory += processed_delivery
