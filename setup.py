import errno
from   os.path    import dirname, join
import re
from   setuptools import setup, find_packages

with open(join(dirname(__file__), 'headerparser', '__init__.py')) as fp:
    for line in fp:
        m = re.search(r'^\s*__version__\s*=\s*([\'"])([^\'"]+)\1\s*$', line)
        if m:
            version = m.group(2)
            break
    else:
        raise RuntimeError('Unable to find own __version__ string')

try:
    with open(join(dirname(__file__), 'README.rst')) as fp:
        long_desc = fp.read()
except EnvironmentError as e:
    if e.errno == errno.ENOENT:
        long_desc = None
    else:
        raise

setup(
    name='headerparser',
    version=version,
    packages=find_packages(),
    license='MIT',
    author='John Thorvald Wodder II',
    author_email='headerparser@varonathe.org',
    keywords='e-mail email mail rfc822 headers rfc2822 rfc5322 parser',
    description='argparse for mail-style headers',
    long_description=long_desc,
    url='https://github.com/jwodder/headerparser',

    setup_requires=['pytest-runner>=2.0,<3'],

    install_requires=[
        'attrs',
        'six',
    ],

    tests_require=['pytest>=2.8,<3', 'pytest-cov>=2.0,<3'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',

        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Usenet News',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Text Processing',
    ],

    entry_points={
        "console_scripts": [
        ]
    },
)
