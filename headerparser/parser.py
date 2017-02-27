from   six       import itervalues, string_types
from   .         import errors
from   .normdict import NormalizedDict
from   .scanner  import scan_file, scan_lines, scan_string
from   .types    import lower
from   .util     import unfold

class HeaderParser(object):
    def __init__(self, normalizer=None, body=None):
        self.normalizer = normalizer or lower
        self.body = body
        self.fielddefs = dict()
        self.dests = set()
        self.additional = None
        self.custom_dests = False

    def add_field(self, name, *altnames, **kwargs):
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
