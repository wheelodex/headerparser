.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active — The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://github.com/jwodder/headerparser/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/headerparser/actions?workflow=Test
    :alt: CI Status

.. image:: https://codecov.io/gh/jwodder/headerparser/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/headerparser

.. image:: https://img.shields.io/pypi/pyversions/headerparser.svg
    :target: https://pypi.org/project/headerparser

.. image:: https://img.shields.io/github/license/jwodder/headerparser.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/headerparser>`_
| `PyPI <https://pypi.org/project/headerparser>`_
| `Documentation <https://headerparser.readthedocs.io>`_
| `Issues <https://github.com/jwodder/headerparser/issues>`_
| `Changelog <https://github.com/jwodder/headerparser/blob/master/CHANGELOG.md>`_

``headerparser`` parses key-value pairs in the style of RFC 822 (e-mail)
headers and converts them into case-insensitive dictionaries with the trailing
message body (if any) attached.  Fields can be converted to other types, marked
required, or given default values using an API based on the standard library's
``argparse`` module.  (Everyone loves ``argparse``, right?)  Low-level
functions for just scanning header fields (breaking them into sequences of
key-value pairs without any further processing) are also included.

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
``headerparser`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install
``headerparser``::

    python3 -m pip install headerparser


Examples
========

Define a parser:

>>> import headerparser
>>> parser = headerparser.HeaderParser()
>>> parser.add_field('Name', required=True)
>>> parser.add_field('Type', choices=['example', 'demonstration', 'prototype'], default='example')
>>> parser.add_field('Public', type=headerparser.BOOL, default=False)
>>> parser.add_field('Tag', multiple=True)
>>> parser.add_field('Data')

Parse some headers and inspect the results:

>>> msg = parser.parse('''\
... Name: Sample Input
... Public: yes
... tag: doctest, examples,
...   whatever
... TAG: README
...
... Wait, why I am using a body instead of the "Data" field?
... ''')
>>> sorted(msg.keys())
['Name', 'Public', 'Tag', 'Type']
>>> msg['Name']
'Sample Input'
>>> msg['Public']
True
>>> msg['Tag']
['doctest, examples,\n  whatever', 'README']
>>> msg['TYPE']
'example'
>>> msg['Data']
Traceback (most recent call last):
    ...
KeyError: 'data'
>>> msg.body
'Wait, why I am using a body instead of the "Data" field?\n'

Fail to parse headers that don't meet your requirements:

>>> parser.parse('Type: demonstration')
Traceback (most recent call last):
    ...
headerparser.errors.MissingFieldError: Required header field 'Name' is not present
>>> parser.parse('Name: Bad type\nType: other')
Traceback (most recent call last):
    ...
headerparser.errors.InvalidChoiceError: 'other' is not a valid choice for 'Type'
>>> parser.parse('Name: unknown field\nField: Value')
Traceback (most recent call last):
    ...
headerparser.errors.UnknownFieldError: Unknown header field 'Field'

Allow fields you didn't even think of:

>>> parser.add_additional()
>>> msg = parser.parse('Name: unknown field\nField: Value')
>>> msg['Field']
'Value'

Just split some headers into names & values and worry about validity later:

>>> for field in headerparser.scan('''\
... Name: Scanner Sample
... Unknown headers: no problem
... Unparsed-Boolean: yes
... CaSe-SeNsItIvE-rEsUlTs: true
... Whitespace around colons:optional
... Whitespace around colons  :  I already said it's optional.
...   That means you have the _option_ to use as much as you want!
...
... And there's a body, too, I guess.
... '''): print(field)
('Name', 'Scanner Sample')
('Unknown headers', 'no problem')
('Unparsed-Boolean', 'yes')
('CaSe-SeNsItIvE-rEsUlTs', 'true')
('Whitespace around colons', 'optional')
('Whitespace around colons', "I already said it's optional.\n  That means you have the _option_ to use as much as you want!")
(None, "And there's a body, too, I guess.\n")
