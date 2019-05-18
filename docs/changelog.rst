.. currentmodule:: headerparser

Changelog
=========

v0.4.0 (in development)
-----------------------
- Added a `scan()` function combining the behavior of `scan_file()` and
  `scan_lines()`, which are now deprecated

v0.3.0 (2018-10-12)
-------------------
- Drop support for Python 3.3
- Gave `HeaderParser` and the scanner functions options for configuring
  scanning behavior:

  - ``separator_regex``
  - ``skip_leading_newlines``

- Fixed a `DeprecationWarning` in Python 3.7

v0.2.0 (2018-02-14)
-------------------
- `NormalizedDict`'s default normalizer (exposed as the `lower()` function) now
  passes non-strings through unchanged
- `HeaderParser` instances can now be compared for non-identity equality
- `HeaderParser.add_field()` and `HeaderParser.add_additional()` now take an
  optional ``action`` argument for customizing the parser's behavior when a
  field is encountered
- Made the `unfold()` function public

v0.1.0 (2017-03-17)
-------------------
Initial release
