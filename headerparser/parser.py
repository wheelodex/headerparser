from   operator  import methodcaller
from   six       import itervalues, string_types
from   .errors   import DuplicateHeaderError, MissingHeaderError, \
                            RedefinitionError, UnknownHeaderError
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
            raise RedefinitionError(header=redefs[0])
        if hd.dest in self.dests:
            raise RedefinitionError(dest=hd.dest)
        for n in normed:
            self.headerdefs[n] = hd
        self.dests.add(hd.dest)
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
                    raise UnknownHeaderError(k)
                hd.process_value(data, v)
        for hd in itervalues(self.headerdefs):
            if hd.dest not in data:
                if hd.required:
                    raise MissingHeaderError(hd.name)
                elif hasattr(hd, 'default'):
                    data[hd.dest] = hd.default
        return data

    def parse_file(self, fp):
        return self._parse_stream(scan_file(fp))

    def parse_string(self, fp):
        return self._parse_stream(scan_string(fp))


class HeaderDef(object):
    def __init__(self, name, dest, type=None, multiple=False, required=False,
                 unfold=False, **kwargs):
        if not isinstance(name, string_types):
            raise TypeError('header names must be strings')
        self.name = name
        self.dest = dest
        self.type = type
        self.multiple = bool(multiple)
        self.required = bool(required)
        self.unfold = bool(unfold)
        if 'default' in kwargs:
            self.default = kwargs.pop('default')
        if kwargs:
            raise TypeError('invalid keyword argument: '
                            + repr(next(iter(kwargs))))

    ###choices  = attr.ib(convert=list, default=None, validator=bool)

    def process_value(self, data, value):
        if self.unfold:
            value = unfold(value)
        if self.type is not None:
            value = self.type(value)
        ### choices
        if self.multiple:
            data.setdefault(self.dest, []).append(value)
        elif self.dest in data:
            raise DuplicateHeaderError(self.name)
        else:
            data[self.dest] = value
