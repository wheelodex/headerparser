import collections
from   six    import iteritems, itervalues
from   .types import lower

class NormalizedDict(collections.MutableMapping):
    """
    A generalization of a case-insensitive dictionary.  `NormalizedDict` takes
    a callable (the "normalizer") that is applied to any key passed to its
    ``__getitem__``, ``__setitem__``, or ``__delitem__`` method, and the result
    of the call is then used for the actual lookup.  When iterating over a
    `NormalizedDict`, each key is returned as the "pre-normalized" form passed
    to ``__setitem__`` the last time the key was set (but see `normalized()`
    below).  Aside from this, `NormalizedDict` behaves like a normal
    `~collections.MutableMapping` class.

    Two `NormalizedDict` instances compare equal iff their normalizers, bodies,
    and `normalized_dict()` return values are equal.  When comparing a
    `NormalizedDict` to any other type of mapping, the other mapping is first
    converted to a `NormalizedDict` using the same normalizer.

    If not specified, the normalizer defaults to
    ``operator.methodcaller('lower')``, so `NormalizedDict` defaults to yet
    another case-insensitive dictionary.  (Note that this default assumes that
    all non-normalized keys are strings, which is true when `HeaderParser` is
    populating the mapping but need not be true when you are using this class
    for your own purposes.)

    :param mapping data: a mapping or iterable of ``(key, value)`` pairs with
        which to initialize the instance
    :param callable normalizer: A callable to apply to keys before looking them
        up; defaults to ``operator.methodcaller('lower')``.  ``normalizer``
        MUST be idempotent (i.e., ``normalizer(x)`` must equal
        ``normalizer(normalizer(x))`` for all inputs) or else bad things will
        happen to your dictionary.
    :param body: initial value for the ``body`` attribute
    :type body: string or `None`
    """

    def __init__(self, data=None, normalizer=None, body=None):
        self._data = {}
        self.normalizer = normalizer or lower
        #: This is where `HeaderParser` stores the message body (if any)
        #: accompanying the header section represented by the main mapping
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
        return (key for key, value in itervalues(self._data))

    def __len__(self):
        return len(self._data)

    def __eq__(self, other):
        if isinstance(other, NormalizedDict):
            if self.normalizer != other.normalizer or self.body != other.body:
                return False
        elif isinstance(other, collections.Mapping):
            if self.body is not None:
                return False
            other = NormalizedDict(other, normalizer=self.normalizer)
        else:
            return NotImplemented
        return self.normalized_dict() == other.normalized_dict()

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):  # pragma: no cover
        return '{0.__class__.__module__}.{0.__class__.__name__}'\
               '({1!r}, normalizer={0.normalizer!r}, body={0.body!r})'\
               .format(self, dict(self))

    def normalized(self):
        return NormalizedDict(
            self.normalized_dict(),
            normalizer=self.normalizer,
            body=self.body,
        )

    def normalized_dict(self):
        return {key: value for key, (_, value) in iteritems(self._data)}

    def copy(self):
        dup = self.__class__()
        dup._data = self._data.copy()
        dup.normalizer = self.normalizer
        dup.body = self.body
        return dup
