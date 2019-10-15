v0.5.0 (in development)
-----------------------
- Support Python 3.8

v0.4.0 (2019-05-29)
-------------------
- Added a `scan()` function combining the behavior of `scan_file()` and
  `scan_lines()`, which are now deprecated
- Gave `HeaderParser` a `parse()` method combining the behavior of
  `parse_file()` and `parse_lines()`, which are now deprecated
- Added `scan_next_stanza()` and `scan_next_stanza_string()` functions for
  scanning & consuming input only up to the end of the first header section
- Added `scan_stanzas()` and `scan_stanzas_string()` functions for scanning
  input composed entirely of multiple stanzas/header sections
- Gave `HeaderParser` `parse_next_stanza()` and `parse_next_stanza_string()`
  methods for parsing & comsuming input only up to the end of the first header
  section
- Gave `HeaderParser` `parse_stanzas()` and `parse_stanzas_string()` methods
  for parsing input composed entirely of multiple stanzas/header sections

v0.3.0 (2018-10-12)
-------------------
- Drop support for Python 3.3
- Gave `HeaderParser` and the scanner functions options for configuring
  scanning behavior:
    - `separator_regex`
    - `skip_leading_newlines`
- Fixed a `DeprecationWarning` in Python 3.7

v0.2.0 (2018-02-14)
-------------------
- `NormalizedDict`'s default normalizer (exposed as the `lower()` function) now
  passes non-strings through unchanged
- `HeaderParser` instances can now be compared for non-identity equality
- `HeaderParser.add_field()` and `HeaderParser.add_additional()` now take an
  optional `action` argument for customizing the parser's behavior when a field
  is encountered
- Made the `unfold()` function public

v0.1.0 (2017-03-17)
-------------------
Initial release
