Stackify API for Python
=======

[Stackify](https://stackify.com) support for Python programs.

```python
import stackify

logger = stackify.getLogger()

try:
    "Make it so, #" + 1
except:
    logger.exception("Can't add strings and numbers")
```

## Install
stackify-python can be installed through pip:
```bash
$ pip install -U stackify
```

You can also check out the repository and install with setuptools:
```bash
$ ./setup.py install
```

## Setup
Your Stackify setup information can be provided via environment variables. For example:
```bash
export STACKIFY_APPLICATION=MyApp
export STACKIFY_ENVIRONMENT=Dev
export STACKIFY_API_KEY=******
```

You can optionally provide your API_URL:
```bash
export STACKIFY_API_URL='http://myapi.stackify.com'
```

These options can also be provided in your code:
```python
import stackify

logger = stackify.getLogger(application="MyApp", environment="Dev", api_key=******)
logger.warning('Something happened')
```

## Usage

Stackify can store extra data along with your log message:
```python
import stackify

logger = stackify.getLogger()

try:
    user_string = raw_input("Enter a number: ")
    print("You entered", int(user_string))
except ValueError:
    logger.exception('Bad input', extra={'user entered': user_string})
```

## Testing
Run the test suite with setuptools:
```bash
$ ./setup.py test
```

You can obtain a coverage report with nose:
```bash
$ ./setup nosetests --with-coverage --cover-package=stackify
```

