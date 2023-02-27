from backend.database import Column, DateTime, Float, Integer, Model, UniqueConstraint


class LoadModel(Model):
    datetime = Column(DateTime())
    value: float = Column(Float())
    component_id = Column(Integer, nullable=False)

    UniqueConstraint(datetime, component_id)

    __abstract__: bool = True
    __repr_props__ = ("id", "component_id", "datetime", "value")

    def get_id(self):
        return self.id


class Load(LoadModel):
    __tablename__ = "load"


class ManualLoad(LoadModel):
    __tablename__ = "manual_load"
