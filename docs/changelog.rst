.. currentmodule:: headerparser

Changelog
=========

v0.6.0 (in development)
-----------------------
- Moved to wheelodex organization
- Migrated from setuptools to hatch


v0.5.1 (2023-10-04)
-------------------
- Include :file:`py.typed` file in distribution


v0.5.0 (2023-10-04)
-------------------
- Support Python 3.8 through 3.12
- Drop support for Python 2.7, 3.4, 3.5, and 3.6
- Removed ``scan_file()``, ``scan_lines()``, ``HeaderParser.parse_file()``, and
  ``HeaderParser.parse_lines()`` (all deprecated in v0.4.0)
- Type annotations added
- The scanner options to the scanner functions are now keyword-only
- `scan()` and `scan_stanzas()` can now parse strings directly.  As a result,
  `scan_string()` and `scan_stanzas_string()` are now deprecated.
- The `HeaderParser` methods `~HeaderParser.parse()` and
  `~HeaderParser.parse_stanzas()` can now parse strings directly.  As a result,
  the `~HeaderParser.parse_string()` and `~HeaderParser.parse_stanzas_string()`
  methods are now deprecated.
- Added a `Scanner` class with methods for scanning a shared input.  As a
  result, the following are now deprecated:

  - `scan_next_stanza()`
  - `scan_next_stanza_string()`
  - `HeaderParser.parse_next_stanza()`
  - `HeaderParser.parse_next_stanza_string()`


v0.4.0 (2019-05-29)
-------------------
- Added a `scan()` function combining the behavior of ``scan_file()`` and
  ``scan_lines()``, which are now deprecated
- Gave `HeaderParser` a `~HeaderParser.parse()` method combining the behavior
  of ``parse_file()`` and ``parse_lines()``, which are now deprecated
- Added `scan_next_stanza()` and `scan_next_stanza_string()` functions for
  scanning & consuming input only up to the end of the first header section
- Added `scan_stanzas()` and `scan_stanzas_string()` functions for scanning
  input composed entirely of multiple stanzas/header sections
- Gave `HeaderParser` `parse_next_stanza()` and `parse_next_stanza_string()`
  methods for parsing & consuming input only up to the end of the first header
  section
- Gave `HeaderParser` `parse_stanzas()` and `parse_stanzas_string()` methods
  for parsing input composed entirely of multiple stanzas/header sections


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
