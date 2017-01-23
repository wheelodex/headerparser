from headerparser import NormalizedDict

def test_empty():
    nd = NormalizedDict()
    assert dict(nd) == {}
    assert nd.body is None

### set & retrieve
### set a key, then set again with different casing
### delitem
### len
### eq
### eq with different normalizers
### normalized()
### normalized_dict()
### different normalizers (identity, hyphens=underscores, titlecase?, etc.)
