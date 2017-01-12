parser = RFC822Parser(body=True, body_dest='__body__', **kwargs)
### **kwargs go to the low-level lexer
### Add some sort of handling for "From " lines
### header name normalization callable (default: str.lower)
### Support comments? (cf. robots.txt)
### object_hook and object_pairs_hook ?

parser.add_header('name', type=callable, multiple=True, dest='key')
parser.add_header('unique', multiple=False, mode='last')
parser.add_header('type', required=True, choices=['good', 'bad'], default='good')

### Remove `dest` and `body_dest`?
#unfold=bool  # If true, newlines are removed from the value before passing it to the `type` callable (if any)
#i18n=bool  # whether to decode i18n(?) encoding before passing to `type`
#action=callable ?
#validator=callable ?
### Support headers with multiple equivalent names

### "default" defaults to `None` if multiple=False, `[]` otherwise

### Add a way to set the type, multiple, etc. for headers not explicitly named (or forbid them completely); `parser.add_defaults()`? `parser.set_defaults()`?

??? = parser.parse(fh)  # parsefile? parse_file?
??? = parser.parsestring(s)

[headers] = parser.parse_stanzas(fh)
[headers] = parser.parse_stanzas_string(s)

### Return a (header_dict, body) pair?
### Return a dict with a `body` attribute?
