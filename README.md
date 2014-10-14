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

## Installation
stackify-python can be installed through pip:
```bash
$ pip install -U stackify
```

You can also check out the repository and install with setuptools:
```bash
$ ./setup.py install
```

## Configuration
Your Stackify setup information can be provided via environment variables. For example:
```bash
export STACKIFY_APPLICATION=MyApp
export STACKIFY_ENVIRONMENT=Dev
export STACKIFY_API_KEY=******
```

These options can also be provided in your code:
```python
import stackify

logger = stackify.getLogger(application="MyApp", environment="Dev", api_key=******)
logger.warning('Something happened')
```

## Usage

stackify-python handles uploads in batches of 100 messages at a time on another thread.
When your program exits, it will shut the thread down and upload the remaining messages.

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
You might need to install the `nose` and `coverage` packages.

