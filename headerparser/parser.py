from   six       import itervalues, string_types
from   .         import errors
from   .normdict import NormalizedDict
from   .scanner  import scan_file, scan_lines, scan_string
from   .types    import lower
from   .util     import unfold

class HeaderParser(object):
    """
    A parser for RFC 822-style header sections.  Define the fields the parser
    should recognize with the `add_field` method, configure handling of
    unrecognized fields with `add_additional`, and then parse input with
    `parse_file` or `parse_string`.

    :param callable normalizer: By default, the parser will consider two field
        names to be equal iff their lowercased forms are equal.  This can be
        overridden by setting ``normalizer`` to a custom callable that takes a
        field name and returns a "normalized" name for use in equality testing.
        The normalizer will also be used when looking up keys in the
        `NormalizedDict` instances returned by the parser's ``parse_*``
        methods.

    :param bool body: whether the parser should allow or forbid a body after
        the header section; `True` means a body is required, `False` means a
        body is prohibited, and `None` means a body is optional
    """

    def __init__(self, normalizer=None, body=None):
        self.normalizer = normalizer or lower
        self.body = body
        self.fielddefs = dict()
        self.dests = set()
        self.additional = None
        self.custom_dests = False

    def add_field(self, name, *altnames, **kwargs):
        """
        Define a header field for the parser to parse.  During parsing, if a
        field is encountered whose name (*modulo* normalization) equals
        ``name`` or is in ``altnames``, the field's value will be processed
        according to the options in ``**kwargs``.  (If no options are
        specified, the value will just be stored in the result dictionary.)

        :param string name: the primary name for the field, used in error
            messages and as the default value of ``dest``

        :param strings altnames: field name synonyms

        :param dest: The key in the result dictionary in which the field's
            value(s) will be stored; defaults to ``name``.  When additional
            headers are enabled (see `add_additional`), ``dest`` can only equal
            one of the field's names.

        :param bool required: If `True` (default `False`), the ``parse_*``
            methods will raise a `~headerparser.errors.MissingFieldError` if
            the field is not present in the input

        :param default: The value to associate with the field if it is not
            present in the input.  If no default value is specified, the field
            will be omitted from the result dictionary if it is not present in
            the input.  ``default`` cannot be set when the field is required.
            ``type`` and ``unfold`` will not be applied to the default value,
            and the default value need not belong to ``choices``.

        :param bool unfold: If `True` (default `False`), the field value will
            be "unfolded" (i.e., line breaks will be removed and whitespace
            around line breaks will be converted to a single space) before
            applying ``type``

        :param callable type: a callable to apply to the field value before
            storing it in the result dictionary

        :param iterable choices: A sequence of values which the field is
            allowed to have.  If ``choices`` is defined, all occurrences of the
            field in the input must have one of the given values (after
            applying ``type``) or else an
            `~headerparser.errors.InvalidChoiceError` is raised.

        :param bool multiple: If `True`, the header field will be allowed to
            occur more than once in the input, and all of the field's values
            will be stored in a list.  If `False` (the default), a
            `~headerparser.errors.DuplicateFieldError` will be raised if the
            field occurs more than once in the input.

        :return: `None`
        :raises ValueError:
            - if another field with the same name or ``dest`` was already
              defined
            - if ``dest`` is not one of the field's names and `add_additional`
              is enabled
            - if ``default`` is defined and ``required`` is true
            - if ``choices`` is an empty sequence
        :raises TypeError: if ``name`` or one of the ``altnames`` is not a
            string
        """

        kwargs.setdefault('dest', name)
        hd = NamedField(name=name, **kwargs)
        normed = set(map(self.normalizer, (name,) + altnames))
        # Error before modifying anything:
        redefs = [n for n in self.fielddefs if n in normed]
        if redefs:
            raise ValueError('field defined more than once: ' + repr(redefs[0]))
        if self.normalizer(hd.dest) in self.dests:
            raise ValueError('destination defined more than once: '
                             + repr(hd.dest))
        if self.normalizer(hd.dest) not in normed:
            if self.additional is not None:
                raise ValueError('add_additional and `dest` are mutually exclusive')
            self.custom_dests = True
        for n in normed:
            self.fielddefs[n] = hd
        self.dests.add(self.normalizer(hd.dest))

    def add_additional(self, allow=True, **kwargs):
        if allow:
            if self.custom_dests:
                raise ValueError('add_additional and `dest` are mutually exclusive')
            self.additional = FieldDef(**kwargs)
        else:
            self.additional = None

    def parse_stream(self, fields):
        data = NormalizedDict(normalizer=self.normalizer)
        for k,v in fields:
            if k is None:
                assert data.body is None
                if self.body is not None and not self.body:
                    raise errors.BodyNotAllowedError()
                data.body = v
            else:
                try:
                    hd = self.fielddefs[self.normalizer(k)]
                except KeyError:
                    if self.additional is not None:
                        hd = self.additional
                    else:
                        raise errors.UnknownFieldError(k)
                hd.process(data, k, v)
        for hd in itervalues(self.fielddefs):
            if hd.dest not in data:
                if hd.required:
                    raise errors.MissingFieldError(hd.name)
                elif hasattr(hd, 'default'):
                    data[hd.dest] = hd.default
        if self.body and data.body is None:
            raise errors.MissingBodyError()
        return data

    def parse_file(self, fp):
        return self.parse_stream(scan_file(fp))

    def parse_lines(self, iterable):
        return self.parse_stream(scan_lines(iterable))

    def parse_string(self, s):
        return self.parse_stream(scan_string(s))


class FieldDef(object):
    def __init__(self, type=None, multiple=False, unfold=False, choices=None):
        self.type = type
        self.multiple = bool(multiple)
        self.unfold = bool(unfold)
        if choices is not None:
            choices = list(choices)
            if not choices:
                raise ValueError('empty list supplied for choices')
        self.choices = choices

    def _process(self, data, name, dest, value):
        if self.unfold:
            value = unfold(value)
        if self.type is not None:
            try:
                value = self.type(value)
            except errors.FieldTypeError:
                raise
            except Exception as e:
                raise errors.FieldTypeError(name, value, e)
        if self.choices is not None and value not in self.choices:
            raise errors.InvalidChoiceError(name, value)
        if self.multiple:
            data.setdefault(dest, []).append(value)
        elif dest in data:
            raise errors.DuplicateFieldError(name)
        else:
            data[dest] = value

    def process(self, data, name, value):
        self._process(data, name, name, value)


class NamedField(FieldDef):
    def __init__(self, name, dest, required=False, **kwargs):
        if not isinstance(name, string_types):
            raise TypeError('field names must be strings')
        self.name = name
        self.dest = dest
        self.required = bool(required)
        if 'default' in kwargs:
            if self.required:
                raise ValueError('required and default are mutually exclusive')
            self.default = kwargs.pop('default')
        super(NamedField, self).__init__(**kwargs)

    def process(self, data, _, value):
        self._process(data, self.name, self.dest, value)
