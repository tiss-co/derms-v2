from backend.extensions import auth


class User(object):
    """The User model.

    The User model is used to authenticate tokens with user management client.

    Parameters
    ----------
    token : str
        The token to authenticate with.
    require_admin_privilege : bool
        Whether the user requires admin privilege or not. Default is `True`.
    """

    __repr_props__: tuple = (
        "token",
        "require_admin_privilege",
    )

    def __init__(self, token: str, require_admin_privilege: bool = True):
        """Initialize the User model."""

        self.token = token
        self.require_admin_privilege = require_admin_privilege

    @classmethod
    def get_by(cls, token: str, require_admin_privilege: bool = True):
        """
        Get User model by token.

        Parameters
        ----------
        token : str
            The token to authenticate with.
        require_admin_privilege : bool
            Whether the user requires admin privilege. Default is `True`.
        """

        return cls(token, require_admin_privilege)

    def has_product_privilege(self, domain: str, product: str):
        """Return True if the user has product privilege."""

        return (
            False
            if not self.token
            else auth.has_prod_perm(
                str(self.token), str(domain), str(product), "View", 0
            )
        )

    def has_ptrack_privilege(self):
        """Return True if the user has pTrack privilege."""

        return self.has_product_privilege(domain="pTrack", product="pTrack")

    def has_admin_privilege(self):
        """Return True if the user has admin privilege."""

        return False if not self.token else auth.is_admin(str(self.token))

    def is_authenticated(self):
        """Return True if the user is authenticated."""

        return (
            self.has_ptrack_privilege()
            if self.require_admin_privilege is False
            else self.has_admin_privilege()
        )

    def __repr__(self) -> str:

        properties = [
            f"{prop}={getattr(self, prop)!r}"
            for prop in self.__repr_props__
            if hasattr(self, prop)
        ]

        return f"<{self.__class__.__name__} {' '.join(properties)}>"
