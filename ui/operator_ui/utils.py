from requests.exceptions import ConnectionError, RequestException


class Attrs:

    @classmethod
    def call(cls, f, **kwargs):
        return f(cls(**kwargs))

    def __init__(self, **kwargs):
        self.attrs = kwargs

    def __getattr__(self, attr):
        return self.attrs.get(attr)


def get_short_error_message(e: Exception):
    '''Generate a reasonable short message why the HTTP request failed'''

    if isinstance(e, RequestException) and e.response is not None:
        # e.g. "401 Unauthorized"
        return '{} {}'.format(e.response.status_code, e.response.reason)
    elif isinstance(e, ConnectionError):
        # e.g. "ConnectionError" or "ConnectTimeout"
        return e.__class__.__name__
    else:
        return str(e)


def identity(value, *_, **__):
    """
    Trivial identity function: return the value passed in its first argument.

    Examples:

    >>> identity(42)
    42

    >>> list(
    ...     filter(
    ...         identity,
    ...         [None, False, True, 0, 1, list(), set(), dict()],
    ...     ),
    ... )
    [True, 1]
    """

    return value


def const(value, *_, **__):
    """
    Given a value, returns a function that simply returns that value.

    Example:
    >>> f = const(42)
    >>> f()
    42
    >>> f()
    42
    """

    return lambda *_, **__: value


def catching(computation, catcher=identity, exception=Exception):
    """
    Catch exceptions.

    Call the provided computation with no arguments.  If it throws an exception
    of the provided exception class (or any exception, if no class is provided),
    return the result of calling the catcher function with the exception as the
    sole argument.  If no catcher function is specified, return the exception.

    Examples:

    Catch a KeyError and return the exception itself:
    >>> catching(lambda: {'foo': 'bar'}['meh'])
    KeyError('meh',)

    Catch a KeyError and return a default value:
    >>> catching(
    ...     computation=lambda: {'foo': 'bar'}['meh'],
    ...     catcher=const('nope'),
    ... )
    'nope'
    """

    try:
        return computation()
    except exception as e:
        return catcher(e)


def defaulting(computation, default=None, exception=Exception):
    """
    Like `catching`, but just return a default value if an exception is caught.

    If no default value is supplied, default to None.

    Examples:

    Catch a KeyError and return a default value, like the `get` method:
    >>> defaulting(lambda: {'foo': 'bar'}['meh'], 'nope')
    'nope'

    Turn a ZeroDivisionError into None:
    >>> defaulting(lambda: 1/0) == None
    True
    """

    return catching(
        computation=computation,
        catcher=const(default),
        exception=exception,
    )


def these(what, where=None):
    """
    Combinator for yielding multiple values with property access.

    Yields from the values generated by an attribute of the given object, or
    the values generated by the given object itself if no attribute key is
    specified.

    Examples:

    No attribute key specified; yields from the given object:
    >>> these(['foo', 'bar'])
    ['foo', 'bar']

    An attribute key is specified; yields from the values generated by the
    specified attribute's value:
    object:
    >>> these({'foo': ['bar', 'baz']}, 'foo')
    ['bar', 'baz']

    An invalid attribute key is specified; yields nothing:
    >>> these({'foo': ['bar', 'baz']}, 'meh')
    []
    """

    if not where:
        return what
    return what[where] if where in what else []
