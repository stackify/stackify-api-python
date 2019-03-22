Stackify API for Python
=======================

## Installation

**stackify-python-api** can be installed through pip:
```bash
$ pip install stackify-api-python
```

## Configuration


#### Standard API
```python
import stackify
logger = stackify.getLogger(application="Python Application", environment="Production", api_key="***")
logger.warning('Something happened')
```

#### Python Logging Integration

```python
import logging
import stackify
logger = logging.getLogger()
stackify_handler = stackify.StackifyHandler(application="Python Application", environment="Production", api_key="***")
logger.addHandler(stackify_handler)
logger.warning('Something happened')
```

#### Environment Settings

```bash
export STACKIFY_APPLICATION=Python Application
export STACKIFY_ENVIRONMENT=Production
export STACKIFY_API_KEY=******
```


## Usage

**stackify-python-api** handles uploads in batches of 100 messages at a time on another thread.
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
