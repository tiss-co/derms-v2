from backend.database import (
    Boolean,
    Column,
    Date,
    Integer,
    Model,
    UniqueConstraint,
    ForeignKey,
)


class Activation(Model):

    __tablename__ = "activations"

    program_id = Column(Integer(), ForeignKey("program.id"))
    date = Column(Date(), index=True)
    status: bool = Column(Boolean())
    is_manual: bool = Column(Boolean(), nullable=False, server_default="false")
    start: int = Column(Integer(), nullable=True)
    end: int = Column(Integer(), nullable=True)
    UniqueConstraint(date, program_id)

    __repr_props__ = (
        "id",
        "program_id",
        "date",
        "status",
        "is_manual",
        "start",
        "end",
    )

    def get_id(self):
        return self.id
