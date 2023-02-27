from backend.database import Column, DateTime, Float, ForeignKey, Integer, Model, UniqueConstraint


class Result(Model):
    __tablename__ = "results"

    battery_id = Column(Integer, ForeignKey("battery.id"), nullable=False)
    datetime = Column(DateTime())
    charging_status: int = Column(Integer())
    power = Column(Float())
    soc = Column(Float())
    utility_power = Column(Float(), nullable=True)
    UniqueConstraint(datetime, battery_id)

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
