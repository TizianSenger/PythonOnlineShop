class Product:
    def __init__(self, product_id, name, description, price):
        self.id = product_id
        self.name = name
        self.description = description
        self.price = price

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            product_id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            price=data.get("price")
        )