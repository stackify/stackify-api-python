#!/usr/bin/env python
from setuptools import setup
import re
import ast

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

setup(
    name='stackify',
    version=version,
    author='Matthew Thompson',
    author_email='chameleonator@gmail.com',
    packages=['stackify'],
    url='https://github.com/stackify/stackify-api-python',
    license=open('LICENSE.txt').readline(),
    description='Stackify API for Python',
    long_description=read_md('README.md'),
    download_url='https://github.com/stackify/stackify-api-python/tarball/0.0.1',
    keywords=['logging', 'stackify', 'exception'],
    classifiers=["Programming Language :: Python"],
    install_requires=[
        'retrying>=1.2.3',
        'requests>=2.4.1'
    ],
    test_suite='tests',
    tests_requires=[
        'mock>=1.0.1',
        'nose==1.3.4'
    ]
)
