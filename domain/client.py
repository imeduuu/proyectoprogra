class Client:
    def __init__(self, id, name, node_id, priority, total_orders=0):
        self.id = id
        self.name = name
        self.node_id = node_id
        self.priority = priority
        self.total_orders = total_orders

    def to_dict(self, role=None):
        return {
            "id": self.id,
            "name": self.name,
            "node_id": self.node_id,
            "priority": self.priority,
            "total_orders": self.total_orders,
            "role": role 
        }
