from setuptools import setup
import re
import ast

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
    url='https://github.com/stackify/stackify-python',
    license=open('LICENSE.txt').readline(),
    description='Stackify API for Python',
    long_description=open('README.md').read(),
    install_requires=[
        'retrying>=1.2.3',
        'requests>=2.4.1'
    ]
)

