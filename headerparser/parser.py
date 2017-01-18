from   operator import methodcaller
import attr
from   six      import string_types

is_str = attr.validators.instance_of(string_types)

@attr.s
class HeaderParser(object):
    normalizer = attr.ib(default=methodcaller('lower'))
    headerdefs = attr.ib(init=False, default=attr.Factory(dict))

    def add_header(self, name, *altnames, **kwargs):
        kwargs.setdefault('default', [] if kwargs.get('multiple') else None)
        hd = HeaderDef(name=name, **kwargs)
        normed = set(map(self.normalizer, altnames))
        normed.add(self.normalizer(name))
        try:
            normed.add(self.normalizer(kwargs['dest']))
        except KeyError:
            pass
        for n in normed:
            if n in self.headerdefs:
                raise ValueError ###
            self.headerdefs[n] = hd


@attr.s
class HeaderDef(object):
    name     = attr.ib(validator=is_str)
    default  = attr.ib()
    type     = attr.ib(default=None)
    multiple = attr.ib(convert=bool, default=False)
    required = attr.ib(convert=bool, default=False)

    #choices
    #dest
    #mode
    #unfold
    #i18n

    def process_value(self, value):
        ### unfold, i18n
        if self.type is not None:
            value = self.type(value)
        ### choices
        return value
