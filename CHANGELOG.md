v0.2.0 (in development)
-----------------------
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
