import datetime

class Order:
    def __init__(self, order_id, origin, destination, path, cost, client_id, priority=1):
        self.id = order_id
        self.origin = origin
        self.destination = destination
        self.path = path
        self.cost = cost
        self.client_id = client_id  
        self.priority = priority
        self.status = "In Progress"
        self.creation_date = datetime.datetime.now()
        self.delivery_date = None

    def complete_order(self):
        self.status = "Delivered"
        self.delivery_date = datetime.datetime.now()

    def to_dict(self, client_name=None):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "client_name": client_name,  
            "origin": self.origin,
            "destination": self.destination,
            "path": " → ".join(self.path),
            "cost": self.cost,
            "priority": self.priority,
            "status": self.status,
            "creation_date": str(self.creation_date),
            "delivery_date": str(self.delivery_date) if self.delivery_date else None
        }
