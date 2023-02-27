from backend.database import Column, Float, Model, String, Integer


class Battery(Model):
    __tablename__ = "battery"
    
    building_id = Column(Integer(), nullable=False)
    component_id = Column(Integer(), nullable=False)
    battery_type = Column(String(), nullable=False)
    soc_max = Column(Float(), nullable=False)
    soc_min = Column(Float(), nullable=False)
    p_max = Column(Float(), nullable=False)
    p_charge_max = Column(Float(), nullable=False)
    feeder_max = Column(Float(), nullable=False)
    charging_margin = Column(Float(), nullable=False)
    first_start_time = Column(Integer(), nullable=False)
    first_end_time = Column(Integer(), nullable=False)
    second_start_time = Column(Integer(), nullable=False)
    second_end_time = Column(Integer(), nullable=False)

    __repr_props__ = (
        "id",
        "building_id",
        "component_id",
        "battery_type",
        "soc_max",
        "soc_min",
        "p_max",
        "p_charge_max",
        "feeder_max",
        "charging_margin",
        "first_start_time",
        "first_end_time",
        "second_start_time",
        "second_end_time",
    )
