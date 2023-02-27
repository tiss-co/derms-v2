from backend.database import Column, Model, DateTime, Float, ForeignKey, Integer


class PowerQuality(Model):
    __tablename__ = "power_quality"

    battery_id = Column(Integer, ForeignKey("battery.id"), nullable=False)
    datetime = Column(DateTime(), index=True, unique=True)
    voltage_utility = Column(Float(), nullable=True)
    voltage_battery = Column(Float(), nullable=True)
    voltage_facility = Column(Float(), nullable=True)
    current_utility = Column(Float(), nullable=True)
    current_battery = Column(Float(), nullable=True)
    current_facility = Column(Float(), nullable=True)

    __repr_props__ = (
        "id",
        "battery_id",
        "datetime",
        "voltage_utility",
        "voltage_battery",
        "voltage_facility",
        "current_utility",
        "current_battery",
        "current_facility",
    )

    def get_id(self):
        return self.id
