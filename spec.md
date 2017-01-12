    HeaderParser(normalizer=None, **kwargs)

- `normalizer` — header name normalization callable (default: str.lower)
- `**kwargs` are passed to low-level lexer.

- `body=bool` ???
- `body_dest='__body__'` ???
- `object_hook` and `object_pairs_hook` ???


    HeaderParser.add_header(name, *altnames, **kwargs)

- `type=callable`
- `multiple=bool`
- `dest=str`
- `mode in ('first', 'last', 'error')`
- `required=bool`
- `choices=seq`
- `default=...` — defaults to `None` if `multiple=False`, `[]` otherwise
- `unfold=bool` — If true, newlines are removed from the value before passing
  it to the `type` callable (if any)
- `i18n=bool` — whether to decode i18n(?) encodings before passing to `type`

- `action=callable` ?
- `validator=callable` ?


    HeaderParser.add_additional(allow=True, **kwargs)

Has all of the arguments of `add_header` except:

- `name`
- `*altnames`
- `dest` (?)
- `required`
- `default`


    HeaderParser.parse(filehandle)  # `parsefile`? `parse_file`?
    HeaderParser.parsestring(s)

Possible return types:

- a `(header_dict, body)` pair
- a dict with a `body` attribute
- ???

Should the dict be a proper `dict` or "normalizing"?


    HeaderParser.parse_stanzas(filehandle)
    HeaderParser.parse_stanzas_string(s)

Return a list (or generator?) of header dicts
