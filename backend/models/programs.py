from backend.database import Column, Model, Integer, String, ForeignKey, Boolean


class Program(Model):
    __tablename__ = "program"

    battery_id = Column(Integer, ForeignKey("battery.id"), nullable=False)
    name = Column(String(), nullable=False)
    priority = Column(Integer(), nullable=False)
    is_global = Column(Boolean(), nullable=False)

    __repr_props__ = (
        "id",
        "battery_id",
        "name",
        "priority",
        "is_global",
    )

    def get_id(self):
        return self.id
