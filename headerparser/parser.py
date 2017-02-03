from   operator  import methodcaller
from   six       import itervalues, string_types
from   .         import errors
from   .normdict import NormalizedDict
from   .scanner  import scan_file, scan_string
from   .util     import unfold

class HeaderParser(object):
    def __init__(self, normalizer=methodcaller('lower'), body=True):
        self.normalizer = normalizer
        self.body = True
        self.headerdefs = dict()
        self.required = []
        self.dests = set()

    def add_header(self, name, *altnames, **kwargs):
        kwargs.setdefault('dest', name)
        hd = HeaderDef(name=name, **kwargs)
        normed = set(map(self.normalizer, (name,) + altnames))
        # Error before modifying anything:
        redefs = [n for n in self.headerdefs if n in normed]
        if redefs:
            raise errors.RedefinitionError(header=redefs[0])
        if self.normalizer(hd.dest) in self.dests:
            raise errors.RedefinitionError(dest=hd.dest)
        for n in normed:
            self.headerdefs[n] = hd
        self.dests.add(self.normalizer(hd.dest))
        if hd.required:
            self.required.append(hd)

    def _parse_stream(self, headers):
        ### Make this public?
        data = NormalizedDict()
        for k,v in headers:
            if k is None:
                assert data.body is None
                data.body = v
            else:
                try:
                    hd = self.headerdefs[self.normalizer(k)]
                except KeyError:
                    raise errors.UnknownHeaderError(k)
                hd.process_value(data, v)
        for hd in itervalues(self.headerdefs):
            if hd.dest not in data:
                if hd.required:
                    raise errors.MissingHeaderError(hd.name)
                elif hasattr(hd, 'default'):
                    data[hd.dest] = hd.default
        return data

    def parse_file(self, fp):
        return self._parse_stream(scan_file(fp))

    def parse_string(self, s):
        return self._parse_stream(scan_string(s))


class HeaderDef(object):
    def __init__(self, name, dest, type=None, multiple=False, required=False,
                 unfold=False, choices=None, **kwargs):
        if not isinstance(name, string_types):
            raise TypeError('header names must be strings')
        self.name = name
        self.dest = dest
        self.type = type
        self.multiple = bool(multiple)
        self.required = bool(required)
        self.unfold = bool(unfold)
        if choices is not None:
            choices = list(choices)
            if not choices:
                raise ValueError('empty list supplied for choices')
        self.choices = choices
        if 'default' in kwargs:
            if self.required:
                raise ValueError('required and default are mutually exclusive')
            self.default = kwargs.pop('default')
        if kwargs:
            raise TypeError('invalid keyword argument: '
                            + repr(next(iter(kwargs))))

    def process_value(self, data, value):
        if self.unfold:
            value = unfold(value)
        if self.type is not None:
            ### TODO: Wrap this in a try: block that reraises errors as
            ### HeaderTypeErrors?
            value = self.type(value)
        if self.choices is not None and value not in self.choices:
            raise errors.InvalidChoiceError(self.name, value)
        if self.multiple:
            data.setdefault(self.dest, []).append(value)
        elif self.dest in data:
            raise errors.DuplicateHeaderError(self.name)
        else:
            data[self.dest] = value
