.. image:: http://www.repostatus.org/badges/latest/wip.svg
    :target: http://www.repostatus.org/#wip
    :alt: Project Status: WIP – Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. image:: https://travis-ci.org/jwodder/headerparser.svg?branch=master
    :target: https://travis-ci.org/jwodder/headerparser

.. image:: https://coveralls.io/repos/github/jwodder/headerparser/badge.svg?branch=master
    :target: https://coveralls.io/github/jwodder/headerparser?branch=master

.. image:: https://img.shields.io/github/license/jwodder/headerparser.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/headerparser>`_
| `Issues <https://github.com/jwodder/headerparser/issues>`_

``headerparser`` parses files containing RFC 822-style ("e-mail") headers and
converts them into case-insensitive dictionaries with the trailing message body
(if any) attached.  Fields can be converted to other types, marked required, or
given default values using an API based on the standard library's ``argparse``
module.  (Everyone loves ``argparse``, right?)  Low-level functions for just
scanning header fields (breaking them into sequences of key-value pairs without
any further processing) are also included.

The Format
==========
RFC 822-style headers are header fields that follow the general format of
e-mail headers as specified by RFC 822 and friends: each field is a line of the
form "``Name: Value``", with long values continued onto multiple lines
("folded") by indenting the extra lines.  A blank line marks the end of the
header section and the beginning of the message body.

This basic grammar has been used by numerous textual formats besides e-mail,
including but not limited to:

- HTTP request & response headers
- Usenet messages
- most Python packaging metadata files
- Debian packaging control files
- ``META-INF/MANIFEST.MF`` files in Java JARs
- a subset of the `YAML <http://www.yaml.org/>`_ serialization format

— all of which this package can parse.


Installation
============
Just use `pip <https://pip.pypa.io>`_ (You have pip, right?) to install
``headerparser`` and its dependencies::

    pip install git+https://github.com/jwodder/headerparser.git
