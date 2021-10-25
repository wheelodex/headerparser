from typing import Any, Type
from mypy.plugin import Plugin
from mypy.plugins.attrs import attr_attrib_makers, attr_class_makers

attr_class_makers.add("headerparser.parscls.parsable")

attr_attrib_makers.add("headerparser.parscls.Field")
attr_attrib_makers.add("headerparser.parscls.MultiField")
attr_attrib_makers.add("headerparser.parscls.ExtraFields")
attr_attrib_makers.add("headerparser.parscls.MultiExtraFields")
attr_attrib_makers.add("headerparser.parscls.BodyField")


class HeaderParserPlugin(Plugin):
    pass


def plugin(_version: Any) -> Type[Plugin]:
    return HeaderParserPlugin
