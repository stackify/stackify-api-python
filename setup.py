#!/usr/bin/env python
import setuptools
import re
import ast

with open("README.md", "r") as fh:
    long_description = fh.read()

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')  # noqa
except ImportError:
    print('warning: pypandoc module not found, could not convert Markdown to RST')
    read_md = lambda f: open(f).read()  # noqa

version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('stackify/__init__.py') as f:
    f = f.read()
    version = ast.literal_eval(version_re.search(f).group(1))

setuptools.setup(
    name='stackify-api-python',
    version=version,
    author='Stackify',
    author_email='support@stackify.com',
    packages=setuptools.find_packages(exclude=("tests", "*tests", "tests*",)),
    url='https://github.com/stackify/stackify-api-python',
    description='Stackify API for Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['logging', 'stackify', 'exception'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'protobuf>=3.9.1',
        'retrying>=1.2.3',
        'requests>=2.4.1',
        'requests-unixsocket>=0.2.0'
    ],
    test_suite='tests',
    tests_requires=[
        'mock>=1.0.1',
        'nose==1.3.4'
    ]
)
