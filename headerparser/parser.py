from   operator  import methodcaller
import attr
from   six       import string_types
from   .normdict import NormalizedDict
from   .scanner  import scan_file, scan_string
from   .util     import unfold

class HeaderParser(object):
    def __init__(self, normalizer=methodcaller('lower'), body=True):
        self.normalizer = normalizer
        self.body = True
        self.headerdefs = dict()
        self.required = []

    def add_header(self, name, *altnames, **kwargs):
        kwargs.setdefault('default', [] if kwargs.get('multiple') else None)
        hd = HeaderDef(name=name, **kwargs)
        normed = set(map(self.normalizer, altnames))
        normed.add(self.normalizer(name))
        try:
            normed.add(self.normalizer(kwargs['dest']))
        except KeyError:
            pass
        if any(n in normed for n in self.headerdefs):
            # Error before modifying anything
            raise ValueError ###
        for n in normed:
            self.headerdefs[n] = hd
        if hd.required:
            self.required.append(hd)

    def _parse_stream(self, headers):
        data = NormalizedDict()
        for k,v in headers:
            try:
                hd = self.headerdefs[self.normalizer(k)]
            except KeyError:
                raise  #####
            data[hd.dest] = v

    def parse_file(self, fp):
        return self._parse_stream(scan_file(fp))

    def parse_string(self, fp):
        return self._parse_stream(scan_string(fp))


@attr.s
class HeaderDef(object):
    name     = attr.ib(validator=attr.validators.instance_of(string_types))
    default  = attr.ib()
    type     = attr.ib(default=None)
    multiple = attr.ib(convert=bool, default=False)
    required = attr.ib(convert=bool, default=False)
    unfold   = attr.ib(convert=bool, default=False)

    #choices
    #dest
    #mode
    #i18n

    def process_value(self, value):
        ### i18n
        if self.unfold:
            value = unfold(value)
        if self.type is not None:
            value = self.type(value)
        ### choices
        return value
