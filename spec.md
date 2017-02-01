    HeaderParser(normalizer=None, body=True, **kwargs)

- `normalizer` — header name normalization callable (default: str.lower)
- `body=bool` — whether `parse_file` and `parse_string` are allowed to find a
  body after the headers
    - `True`: body is required
    - `False`: body is prohibited
    - `None`: body is optional
- `**kwargs` are passed to low-level scanner


    HeaderParser.add_header(name, *altnames, **kwargs)

- `type=callable`
- `multiple=bool`
- `dest=str` — Prohibited when additional headers are allowed
- `required=bool`
- `choices=seq` — applied after `type`
- `default=...` — Prohibited when `required=True`?
- `unfold=bool` — If true, newlines are removed from the value before passing
  it to the `type` callable (if any)


    HeaderParser.add_additional(allow=True, **kwargs)

Has all of the arguments of `add_header` except:

- `name`
- `*altnames`
- `dest`
- `required`
- `default`


    HeaderParser.parse_file(filehandle)
    HeaderParser.parse_string(s)

Return type: a mapping object with a `body` attribute that normalizes keys on
lookup

- If `body` is `False` and the headers are followed by anything other than
  whitespace, an error is raised


    HeaderParser.parse_stanzas_file(filehandle)
    HeaderParser.parse_stanzas_string(s)

Return a list (or generator?) of header dicts

- `body` attribute is ignored
