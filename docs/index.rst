.. module:: headerparser

==============================================
headerparser — argparse for mail-style headers
==============================================

`GitHub <https://github.com/wheelodex/headerparser>`_
| `PyPI <https://pypi.org/project/headerparser>`_
| `Documentation <https://headerparser.readthedocs.io>`_
| `Issues <https://github.com/wheelodex/headerparser/issues>`_
| :doc:`Changelog <changelog>`

.. toctree::
    :hidden:

    format
    parser
    scanner
    util
    errors
    changelog

`headerparser` parses key-value pairs in the style of :rfc:`822` (e-mail)
headers and converts them into case-insensitive dictionaries with the trailing
message body (if any) attached.  Fields can be converted to other types, marked
required, or given default values using an API based on the standard library's
`argparse` module.  (Everyone loves `argparse`, right?)  Low-level functions
for just scanning header fields (breaking them into sequences of key-value
pairs without any further processing) are also included.

Installation
============
``headerparser`` requires Python 3.10 or higher.  Just use `pip
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


Indices and tables
==================
* :ref:`genindex`
* :ref:`search`
