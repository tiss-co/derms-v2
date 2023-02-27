from backend.database import Column, Model, DateTime, Float, Integer, ForeignKey


class Result(Model):
    __tablename__ = "results"

    battery_id = Column(Integer, ForeignKey("battery.id"), nullable=False)
    datetime = Column(DateTime(), index=True, unique=True)
    charging_status: int = Column(Integer())
    power = Column(Float())
    soc = Column(Float())
    utility_power = Column(Float(), nullable=True)

    __repr_props__ = (
        "id",
        "battery_id",
        "datetime",
        "charging_status",
        "power",
        "soc",
    )

    def get_id(self):
        return self.id
