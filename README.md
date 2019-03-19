Stackify API for Python
=======================

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
# Standard API
import stackify

logger = stackify.getLogger(application="MyApp", environment="Dev", api_key=******)
logger.warning('Something happened')
```

```python
# Python Logging Integration
import logging
import stackify

# your existing logging
logger = logging.getLogger()
...

stackify_handler = stackify.StackifyHandler(application="MyApp", environment="Dev", api_key=******)
logger.addHandler(stackify_handler)

logger.warning('Something happened')
```

## Usage

stackify-python handles uploads in batches of 100 messages at a time on another thread.
When your program exits, it will shut the thread down and upload the remaining messages.

Stackify can store extra data along with your log message:
```python
try:
    user_string = raw_input("Enter a number: ")
    print("You entered", int(user_string))
except ValueError:
    logger.exception('Bad input', extra={'user entered': user_string})
```

You can also name your logger instead of using the automatically generated one:
```python
import stackify

logger = stackify.getLogger('mymodule.myfile')
```

## Internal Logger

This library has an internal logger it uses for debugging and messaging.
For example, if you want to enable debug messages:
```python
import logging

logging.getLogger('stackify').setLevel(logging.DEBUG)
```

By default, it will enable the default logging settings via `logging.basicConfig()`
and print `WARNING` level messages and above. If you wish to set everything up yourself,
just pass `basic_config=False` in `getLogger`:
```python
import stackify

logger = stackify.getLogger(basic_config=False)
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

