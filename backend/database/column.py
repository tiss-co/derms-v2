from backend.extensions import db


class Column(db.Column):
    """
    Overridden to make nullable False by default
    """

    inherit_cache = True

    def __init__(self, *args, nullable=False, **kwargs):
        super().__init__(*args, nullable=nullable, **kwargs)
