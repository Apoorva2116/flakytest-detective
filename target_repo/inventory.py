class Inventory:
    def __init__(self): self.items = {}
    def add(self, name, qty=1): self.items[name] = self.items.get(name, 0) + qty
    def remove(self, name, qty=1):
        if self.items.get(name, 0) < qty: return False
        self.items[name] -= qty
        return True
    def total(self): return sum(self.items.values())
    def snapshot(self): return dict(self.items)
