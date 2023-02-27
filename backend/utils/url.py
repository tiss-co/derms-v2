import unicodedata
from urllib.parse import (
    ParseResult,
    SplitResult,
    _coerce_args,
    _splitnetloc,
    _splitparams,
    scheme_chars,
    uses_params,
)


def is_safe_url(url: str, allowed_hosts: set, require_https: bool = False) -> bool:
    """
    Return ```True``` if the url is a safe redirection (i.e. it doesn't point to
    a different host and uses a safe scheme).

    Always return ```False``` on an empty url.

    If ```require_https``` is set to ```True```, only 'https' will be considered a valid
    scheme, as opposed to 'http' and 'https' with the default, ```False```.

    Parameters
    ----------
    url : str
        The URL to check.
    allowed_hosts : set
        The list of allowed hosts.
    require_https : bool, optional
        Whether to require HTTPS, by default ```False```.

    Examples
    --------
    >>> is_safe_url('http://example.com/path/file.html', {'example.com'})
    True
    >>> is_safe_url('http://example2.com/path/file.html', {'example.com'})
    False
    >>> is_safe_url('https://example.com/path/file.html', {'example.com'})
    True
    >>> is_safe_url('http://example.com/path/file.html', {'example.com'}, require_https=True)
    False
    >>> is_safe_url('https://example.com/path/file.html', {'example.com'}, require_https=True)
    True

    Returns
    -------
    bool
        ```True``` if the url is safe, ```False``` otherwise.

    References
    ----------
    [1] https://github.com/django/django/blob/4bc10b79551f4a7b2e4ad3369873827b70ae42ae/django/utils/http.py (Django 2.2.x)
    """

    if url is not None:
        url = url.strip()

    if not url:
        return False

    if allowed_hosts is None:
        allowed_hosts = set()
    elif isinstance(allowed_hosts, str):
        allowed_hosts = {allowed_hosts}

    # Chrome treats \ completely as / in paths but it could be part of some
    # basic auth credentials so we need to check both URLs.
    return _is_safe_url(
        url, allowed_hosts, require_https=require_https
    ) and _is_safe_url(
        url.replace("\\", "/"), allowed_hosts, require_https=require_https
    )


# Copied from urllib.parse.urlparse() but uses fixed urlsplit() function.
def _urlparse(url: str, scheme: str = "", allow_fragments: bool = True) -> ParseResult:
    """
    Parse a URL into 6 components:
        <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
    Note that we don't break the components up in smaller bits
    (e.g. netloc is a single string) and we don't expand % escapes.

    Parameters
    ----------
    url : str
        The URL to parse.
    scheme : str, default ```""```
        The default scheme to use if the URL is relative and missing a scheme.
    allow_fragments : bool, optional
        Whether to allow fragments in the URL, by default ```True```.

    Examples
    --------
    >>> _urlparse('http://example.com/path/file.html')
    ParseResult(scheme='http', netloc='example.com', path='/path/file.html', ...)

    Returns
    -------
    ParseResult
        A 6-tuple containing the following components of the URL:
        (scheme, netloc, path, params, query, fragment).

    References
    ----------
    [1] https://github.com/django/django/blob/4bc10b79551f4a7b2e4ad3369873827b70ae42ae/django/utils/http.py (Django 2.2.x)
    """

    url, scheme, _coerce_result = _coerce_args(url, scheme)
    splitresult = _urlsplit(url, scheme, allow_fragments)
    scheme, netloc, url, query, fragment = splitresult

    if scheme in uses_params and ";" in url:
        url, params = _splitparams(url)
    else:
        params = ""

    result = ParseResult(scheme, netloc, url, params, query, fragment)

    return _coerce_result(result)


# Copied from urllib.parse.urlsplit() with
# https://github.com/python/cpython/pull/661 applied.
def _urlsplit(url: str, scheme: str = "", allow_fragments: bool = True) -> SplitResult:
    """
    Parse a URL into 5 components:
        <scheme>://<netloc>/<path>?<query>#<fragment>

    Note that we don't break the components up in smaller bits
    (e.g. netloc is a single string) and we don't expand % escapes.

    Parameters
    ----------
    url : str
        The URL to parse.
    scheme : str, default ```""```
        The default scheme to use if the URL is relative and missing a scheme.
    allow_fragments : bool, optional
        Whether to allow fragments in the URL, by default ```True```.

    Examples
    --------
    >>> _urlsplit('http://example.com/path/file.html')
    SplitResult(scheme='http', netloc='example.com', path='/path/file.html', ...)

    Returns
    -------
    SplitResult
        A 5-tuple containing the following components of the URL:
        (scheme, netloc, path, query, fragment).

    Raises
    ------
    ValueError
        - Invalid IPv6 URL.

    References
    ----------
    [1] https://github.com/django/django/blob/4bc10b79551f4a7b2e4ad3369873827b70ae42ae/django/utils/http.py (Django 2.2.x)
    """

    url, scheme, _coerce_result = _coerce_args(url, scheme)
    netloc = query = fragment = ""
    i = url.find(":")

    if i > 0:
        for c in url[:i]:
            if c not in scheme_chars:
                break
        else:
            scheme, url = url[:i].lower(), url[i + 1 :]

    if url[:2] == "//":
        netloc, url = _splitnetloc(url, 2)
        if ("[" in netloc and "]" not in netloc) or (
            "]" in netloc and "[" not in netloc
        ):
            raise ValueError("Invalid IPv6 URL")
    if allow_fragments and "#" in url:
        url, fragment = url.split("#", 1)

    if "?" in url:
        url, query = url.split("?", 1)

    v = SplitResult(scheme, netloc, url, query, fragment)

    return _coerce_result(v)


def _is_safe_url(url: str, allowed_hosts: set, require_https: bool = False) -> bool:
    """A Private function that checks to see if the url is safe.

    Checks to see if the url is a safe redirection URL.

    Parameters
    ----------
    url : str
        The URL to check.
    allowed_hosts : set
        The list of allowed hosts.
    require_https : bool, optional
        Whether to require HTTPS, by default ```False```.

    Returns
    -------
    bool
        ```True``` if the url is safe, ```False``` otherwise.

    References
    ----------
    [1] https://github.com/django/django/blob/4bc10b79551f4a7b2e4ad3369873827b70ae42ae/django/utils/http.py (Django 2.2.x)
    """

    # Chrome considers any URL with more than two slashes to be absolute, but
    # urlparse is not so flexible. Treat any url with three slashes as unsafe.

    if url.startswith("///"):
        return False
    try:
        url_info = _urlparse(url)
    except ValueError:  # e.g. invalid IPv6 addresses
        return False

    # Forbid URLs like http:///example.com - with a scheme, but without a hostname.
    # In that URL, example.com is not the hostname but, a path component. However,
    # Chrome will still consider example.com to be the hostname, so we must not
    # allow this syntax.
    if not url_info.netloc and url_info.scheme:
        return False

    # Forbid URLs that start with control characters. Some browsers (like
    # Chrome) ignore quite a few control characters at the start of a
    # URL and might consider the URL as scheme relative.
    if unicodedata.category(url[0])[0] == "C":
        return False

    scheme = url_info.scheme

    # Consider URLs without a scheme (e.g. //example.com/p) to be http.
    if not url_info.scheme and url_info.netloc:
        scheme = "http"

    valid_schemes = ["https"] if require_https else ["http", "https"]

    return (not url_info.netloc or url_info.netloc in allowed_hosts) and (
        not scheme or scheme in valid_schemes
    )
