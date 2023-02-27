from backend.database import Column, DateTime, Float, Model, String, ForeignKey, Integer


class BatteryDetails(Model):
    __tablename__ = "battery_details"

    battery_id = Column(Integer, ForeignKey("battery.id"), nullable=False)
    datetime = Column(DateTime(), index=True, unique=True)
    current_status = Column(String(), nullable=True)
    p_max = Column(Float(), nullable=True)
    p_max_charge = Column(Float(), nullable=True)
    capacity = Column(Float(), nullable=True)
    available_energy = Column(Float(), nullable=True)
    state_of_charge = Column(Float(), nullable=True)
    remaining_life_cycle = Column(Float(), nullable=True)
    state_of_health = Column(Float(), nullable=True)
    grid_frequency = Column(Float(), nullable=True)
    average_grid_current = Column(Float(), nullable=True)
    reactive_power = Column(Float(), nullable=True)
    ambient_temperature = Column(Float(), nullable=True)
    power_factor = Column(Float(), nullable=True)

    __repr_props__ = (
        "id",
        "battery_id",
        "current_status",
        "p_max",
        "p_max_charge",
        "capacity",
        "available_energy",
        "state_of_charge",
        "remaining_life_cycle",
        "state_of_health",
        "grid_frequency",
        "average_grid_current",
        "reactive_power",
        "ambient_temperature",
        "power_factor",
    )

    def get_id(self):
        return self.id
