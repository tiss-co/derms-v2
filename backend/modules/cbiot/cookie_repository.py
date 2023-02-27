import os
import pickle

from .settings import COOKIE_PATH


class CookieRepository(object):
    """Class to act as a cookie repository."""

    @staticmethod
    def save(cookies, cookie_name):
        """
        Save the cookies to the cookie repository.
        Parameters
        ----------
        cookies
        cookie_name: str
            The name of the cookie.
        Returns
        -------
        None
        """
        CookieRepository._ensure_cookies_dir()
        cookiejar_filepath = CookieRepository._get_cookies_filepath(cookie_name)
        with open(cookiejar_filepath, "wb") as cookie_file:
            pickle.dump(cookies, cookie_file)

    @staticmethod
    def delete(cookie_name):
        """
        Delete the cookie jar file.
        Parameters
        ----------
        cookie_name: str
            The name of the cookie jar file.

        Returns
        -------
        None
        """
        CookieRepository._ensure_cookies_dir()
        cookiejar_filepath = CookieRepository._get_cookies_filepath(cookie_name)
        try:
            os.remove(cookiejar_filepath)
        except FileNotFoundError:
            raise FileNotFoundError("Cookie file not found.")

    @staticmethod
    def get(cookie_name):
        """
        Get the cookies for the given cookie_name.
        Parameters
        ----------
        cookie_name: str
            The name of the cookie.

        Returns
        -------
        cookie: str
        """
        cookies = CookieRepository._load_cookies_from_cache(cookie_name)
        return cookies

    @staticmethod
    def _ensure_cookies_dir():
        """
        Ensure that the cookies directory exists.
        Returns
        -------
        None
        """
        if not os.path.exists(COOKIE_PATH):
            os.makedirs(COOKIE_PATH)

    @staticmethod
    def _get_cookies_filepath(cookie_name):
        """
        Returns the filepath of the cookie jar file.
        Parameters
        ----------
        cookie_name: name of the cookie jar file

        Returns
        -------
        str: filepath of the cookie jar file
        """

        return "{}{}.jr".format(COOKIE_PATH, cookie_name)

    @staticmethod
    def _load_cookies_from_cache(cookie_name):
        """
        Load the cookies from the cache.
        Parameters
        ----------
        cookie_name: str
            The name of the cookie.

        Returns
        -------
        cookies: str
        """
        cookiejar_filepath = CookieRepository._get_cookies_filepath(cookie_name)
        try:
            with open(cookiejar_filepath, "rb") as f:
                cookies = pickle.load(f)
                return cookies
        except FileNotFoundError:
            raise FileNotFoundError("Cookie not found.")
