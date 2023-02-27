from backend.database import (
    Column,
    Model,
    DateTime,
    Date,
    String,
    JSON,
    Enum,
    ForeignKey,
    Integer,
)
import enum


class Action(enum.Enum):
    accept = 1
    reject = 2
    idle = 3


class Alarm(Model):
    __tablename__ = "alarms"

    battery_id = Column(Integer, ForeignKey("battery.id"), nullable=False)
    date = Column(Date(), index=True, nullable=False)
    program_id = Column(Integer, ForeignKey("program.id"), nullable=False)
    content = Column(JSON, nullable=False)
    receive_time = Column(DateTime(), nullable=True)
    clear_time = Column(DateTime(), nullable=True)
    action = Column(Enum(Action))

    __repr_props__ = (
        "id",
        "battery_id",
        "date",
        "program_id",
        "content",
        "receive_time",
        "clear_time",
        "action",
    )

    def get_id(self):
        """Return the activation entity id."""
        return self.id
