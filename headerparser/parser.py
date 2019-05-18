from   six       import itervalues, string_types
from   .         import errors
from   .normdict import NormalizedDict
from   .scanner  import scan, scan_string
from   .types    import lower, unfold

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
        body is prohibited, and `None` (the default) means a body is optional

    :param kwargs: :ref:`scanner options <scan_opts>`
    """

    def __init__(self, normalizer=None, body=None, **kwargs):
        #: The ``normalizer`` argument passed to the constructor, or `lower` if
        #: no normalizer was supplied
        self._normalizer = normalizer or lower
        #: The ``body`` argument passed to the constructor
        self._body = body
        #: Scanner options
        self._scan_opts = kwargs
        #: A mapping from normalized field names to `NamedField` instances
        self._fielddefs = dict()
        #: The set of all normalized ``dest`` values for all named fields
        #: defined so far
        self._dests = set()
        #: If additional fields are enabled, this is the `FieldDef` instance
        #: used to process them; otherwise, it is `None`.
        self._additional = None
        #: Whether any fields with custom ``dest`` values have been defined,
        #: thereby precluding `add_additional()`
        self._custom_dests = False

    def __eq__(self, other):
        if type(self) is type(other):
            return vars(self) == vars(other)
        else:
            return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def add_field(self, name, *altnames, **kwargs):
        """
        Define a header field for the parser to parse.  During parsing, if a
        field is encountered whose name (*modulo* normalization) equals either
        ``name`` or one of the ``altnames``, the field's value will be
        processed according to the options in ``**kwargs``.  (If no options are
        specified, the value will just be stored in the result dictionary.)

        .. versionadded:: 0.2.0
            ``action`` argument added

        :param string name: the primary name for the field, used in error
            messages and as the default value of ``dest``

        :param strings altnames: field name synonyms

        :param dest: The key in the result dictionary in which the field's
            value(s) will be stored; defaults to ``name``.  When additional
            headers are enabled (see `add_additional`), ``dest`` must equal
            (after normalization) one of the field's names.

        :param bool required: If `True` (default `False`), the ``parse_*``
            methods will raise a `~headerparser.errors.MissingFieldError` if
            the field is not present in the input

        :param default: The value to associate with the field if it is not
            present in the input.  If no default value is specified, the field
            will be omitted from the result dictionary if it is not present in
            the input.  ``default`` cannot be set when the field is required.
            ``type``, ``unfold``, and ``action`` will not be applied to the
            default value, and the default value need not belong to
            ``choices``.

        :param bool multiple: If `True`, the header field will be allowed to
            occur more than once in the input, and all of the field's values
            will be stored in a list.  If `False` (the default), a
            `~headerparser.errors.DuplicateFieldError` will be raised if the
            field occurs more than once in the input.

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

        :param callable action: A callable to invoke whenever the field is
            encountered in the input.  The callable will be passed the current
            dictionary of header fields, the field's ``name``, and the field's
            value (after processing with ``type`` and ``unfold`` and checking
            against ``choices``).  The callable replaces the default behavior
            of storing the field's values in the result dictionary, and so the
            callable must explicitly store the values if desired.  When
            ``action`` is defined for a field, ``dest`` cannot be.

        :return: `None`
        :raises ValueError:
            - if another field with the same name or ``dest`` was already
              defined
            - if ``dest`` is not one of the field's names and `add_additional`
              is enabled
            - if ``default`` is defined and ``required`` is true
            - if ``choices`` is an empty sequence
            - if both ``dest`` and ``action`` are defined
        :raises TypeError: if ``name`` or one of the ``altnames`` is not a
            string
        """

        if 'action' in kwargs and 'dest' in kwargs:
            raise ValueError('`action` and `dest` are mutually exclusive')
        kwargs.setdefault('dest', name)
        hd = NamedField(name=name, **kwargs)
        normed = set(map(self._normalizer, (name,) + altnames))
        # Error before modifying anything:
        redefs = [n for n in self._fielddefs if n in normed]
        if redefs:
            raise ValueError('field defined more than once: ' + repr(redefs[0]))
        if self._normalizer(hd.dest) in self._dests:
            raise ValueError('destination defined more than once: '
                             + repr(hd.dest))
        if self._normalizer(hd.dest) not in normed:
            if self._additional is not None:
                raise ValueError('add_additional and `dest` are mutually exclusive')
            self._custom_dests = True
        for n in normed:
            self._fielddefs[n] = hd
        self._dests.add(self._normalizer(hd.dest))

    def add_additional(self, enable=True, **kwargs):
        """
        Specify how the parser should handle fields in the input that were not
        previously registered with `add_field`.  By default, unknown fields
        will cause the ``parse_*`` methods to raise an
        `~headerparser.errors.UnknownFieldError`, but calling this method with
        ``enable=True`` (the default) will change the parser's behavior so that
        all unregistered fields are processed according to the options in
        ``**kwargs``.  (If no options are specified, the additional values will
        just be stored in the result dictionary.)

        If this method is called more than once, only the settings from the
        last call will be used.

        Note that additional field values are always stored in the result
        dictionary using their field name as the key, and two fields are
        considered the same (for the purposes of ``multiple``) iff their names
        are the same after normalization.  Customization of the dictionary key
        and field name can only be done through `add_field`.

        .. versionadded:: 0.2.0
            ``action`` argument added

        :param bool enable: whether the parser should accept input fields that
            were not registered with `add_field`; setting this to `False`
            disables additional fields and restores the parser's default
            behavior

        :param bool multiple: If `True`, each additional header field will be
            allowed to occur more than once in the input, and each field's
            values will be stored in a list.  If `False` (the default), a
            `~headerparser.errors.DuplicateFieldError` will be raised if an
            additional field occurs more than once in the input.

        :param bool unfold: If `True` (default `False`), additional field
            values will be "unfolded" (i.e., line breaks will be removed and
            whitespace around line breaks will be converted to a single space)
            before applying ``type``

        :param callable type: a callable to apply to additional field values
            before storing them in the result dictionary

        :param iterable choices: A sequence of values which additional fields
            are allowed to have.  If ``choices`` is defined, all additional
            field values in the input must have one of the given values (after
            applying ``type``) or else an
            `~headerparser.errors.InvalidChoiceError` is raised.

        :param callable action: A callable to invoke whenever the field is
            encountered in the input.  The callable will be passed the current
            dictionary of header fields, the field's name, and the field's
            value (after processing with ``type`` and ``unfold`` and checking
            against ``choices``).  The callable replaces the default behavior
            of storing the field's values in the result dictionary, and so the
            callable must explicitly store the values if desired.

        :return: `None`
        :raises ValueError:
            - if ``enable`` is true and a previous call to `add_field` used a
              custom ``dest``
            - if ``choices`` is an empty sequence
        """
        if enable:
            if self._custom_dests:
                raise ValueError('add_additional and `dest` are mutually exclusive')
            self._additional = FieldDef(**kwargs)
        else:
            self._additional = None

    def parse_stream(self, fields):
        """
        Process a sequence of ``(name, value)`` pairs as returned by `scan()`
        and return a dictionary of header fields (possibly with body attached).
        This is a low-level method that you will usually not need to call.

        :param fields: a sequence of ``(name, value)`` pairs representing the
            input fields
        :type fields: iterable of pairs of strings
        :rtype: NormalizedDict
        :raises ParserError: if the input fields do not conform to the field
            definitions declared with `add_field` and `add_additional`
        :raises ValueError: if the input contains more than one body pair
        """
        data = NormalizedDict(normalizer=self._normalizer)
        fields_seen = set()
        body_seen = False
        for k,v in fields:
            if k is None:
                if body_seen:
                    raise ValueError('Body appears twice in input')
                if self._body is not None and not self._body:
                    raise errors.BodyNotAllowedError()
                data.body = v
                body_seen = True
            else:
                try:
                    hd = self._fielddefs[self._normalizer(k)]
                except KeyError:
                    if self._additional is not None:
                        hd = self._additional
                    else:
                        raise errors.UnknownFieldError(k)
                else:
                    fields_seen.add(hd.name)
                hd.process(data, k, v)
        for hd in itervalues(self._fielddefs):
            if hd.name not in fields_seen:
                if hd.required:
                    raise errors.MissingFieldError(hd.name)
                elif hasattr(hd, 'default'):
                    data[hd.dest] = hd.default
        if self._body and not body_seen:
            raise errors.MissingBodyError()
        return data

    def parse_file(self, fp):
        """
        Parse an RFC 822-style header field section (possibly followed by a
        message body) from the contents of the given filehandle and return a
        dictionary of the header fields (possibly with body attached)

        :param fp: the file to parse
        :type fp: file-like object
        :rtype: NormalizedDict
        :raises ParserError: if the input fields do not conform to the field
            definitions declared with `add_field` and `add_additional`
        :raises ScannerError: if the header section is malformed
        """
        return self.parse_stream(scan(fp, **self._scan_opts))

    def parse_lines(self, iterable):
        """
        Parse an RFC 822-style header field section (possibly followed by a
        message body) from the given sequence of lines and return a dictionary
        of the header fields (possibly with body attached).  Newlines will be
        inserted where not already present in multiline header fields but will
        not be inserted inside the body.

        :param iterable: a sequence of lines comprising the text to parse
        :type iterable: iterable of strings
        :rtype: NormalizedDict
        :raises ParserError: if the input fields do not conform to the field
            definitions declared with `add_field` and `add_additional`
        :raises ScannerError: if the header section is malformed
        """
        return self.parse_stream(scan(iterable, **self._scan_opts))

    def parse_string(self, s):
        """
        Parse an RFC 822-style header field section (possibly followed by a
        message body) from the given string and return a dictionary of the
        header fields (possibly with body attached)

        :param string s: the text to parse
        :rtype: NormalizedDict
        :raises ParserError: if the input fields do not conform to the field
            definitions declared with `add_field` and `add_additional`
        :raises ScannerError: if the header section is malformed
        """
        return self.parse_stream(scan_string(s, **self._scan_opts))


class FieldDef(object):
    def __init__(self, type=None, multiple=False, unfold=False, choices=None,
                       action=None):
        self.type = type
        self.multiple = bool(multiple)
        self.unfold = bool(unfold)
        if choices is not None:
            choices = list(choices)
            if not choices:
                raise ValueError('empty list supplied for choices')
        self.choices = choices
        self.action = action

    def __eq__(self, other):
        if type(self) is type(other):
            return vars(self) == vars(other)
        else:
            return NotImplemented

    def __ne__(self, other):
        return not (self == other)

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
        if self.action is not None:
            self.action(data, name, value)
        elif self.multiple:
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
