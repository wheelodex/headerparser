from collections.abc import Mapping, MutableMapping
from .types          import lower

class NormalizedDict(MutableMapping):
    """
    A generalization of a case-insensitive dictionary.  `NormalizedDict` takes
    a callable (the "normalizer") that is applied to any key passed to its
    `~object.__getitem__`, `~object.__setitem__`, or `~object.__delitem__`
    method, and the result of the call is then used for the actual lookup.
    When iterating over a `NormalizedDict`, each key is returned as the
    "pre-normalized" form passed to `~object.__setitem__` the last time the key
    was set (but see `normalized()` below).  Aside from this, `NormalizedDict`
    behaves like a normal `~collections.abc.MutableMapping` class.

    If a normalizer is not specified upon instantiation, a default will be used
    that converts strings to lowercase and leaves everything else unchanged, so
    `NormalizedDict` defaults to yet another case-insensitive dictionary.

    Two `NormalizedDict` instances compare equal iff their normalizers, bodies,
    and `normalized_dict()` return values are equal.  When comparing a
    `NormalizedDict` to any other type of mapping, the other mapping is first
    converted to a `NormalizedDict` using the same normalizer.

    :param mapping data: a mapping or iterable of ``(key, value)`` pairs with
        which to initialize the instance
    :param callable normalizer: A callable to apply to keys before looking them
        up; defaults to `lower`.  The callable MUST be idempotent (i.e.,
        ``normalizer(x)`` must equal ``normalizer(normalizer(x))`` for all
        inputs) or else bad things will happen to your dictionary.
    :param body: initial value for the `body` attribute
    :type body: string or `None`
    """

    def __init__(self, data=None, normalizer=None, body=None):
        self._data = {}
        self.normalizer = normalizer or lower
        #: This is where `HeaderParser` stores the message body (if any)
        #: accompanying the header section represented by the mapping
        self.body = body
        if data is not None:
            # Don't call `update` until after `normalizer` is set.
            self.update(data)

    def __getitem__(self, key):
        return self._data[self.normalizer(key)][1]

    def __setitem__(self, key, value):
        self._data[self.normalizer(key)] = (key, value)

    def __delitem__(self, key):
        del self._data[self.normalizer(key)]

    def __iter__(self):
        return (key for key, value in self._data.values())

    def __len__(self):
        return len(self._data)

    def __eq__(self, other):
        if isinstance(other, NormalizedDict):
            if self.normalizer != other.normalizer or self.body != other.body:
                return False
        elif isinstance(other, Mapping):
            if self.body is not None:
                return False
            other = NormalizedDict(other, normalizer=self.normalizer)
        else:
            return NotImplemented
        return self.normalized_dict() == other.normalized_dict()

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return '{0.__module__}.{0.__name__}'\
               '({2!r}, normalizer={1.normalizer!r}, body={1.body!r})'\
               .format(type(self), self, dict(self))

    def normalized(self):
        """
        Return a copy of the instance such that iterating over it will return
        normalized keys instead of the keys passed to `~object.__setitem__`

        >>> normdict = NormalizedDict()
        >>> normdict['Foo'] = 23
        >>> normdict['bar'] = 42
        >>> sorted(normdict)
        ['Foo', 'bar']
        >>> sorted(normdict.normalized())
        ['bar', 'foo']

        :rtype: NormalizedDict
        """
        return NormalizedDict(
            self.normalized_dict(),
            normalizer=self.normalizer,
            body=self.body,
        )

    def normalized_dict(self):
        """
        Convert to a `dict` with all keys normalized.  (A `dict` with
        non-normalized keys can be obtained with ``dict(normdict)``.)

        :rtype: dict
        """
        return {key: value for key, (_, value) in self._data.items()}

    def copy(self):
        """ Create a shallow copy of the mapping """
        dup = type(self)()
        dup._data = self._data.copy()
        dup.normalizer = self.normalizer
        dup.body = self.body
        return dup
