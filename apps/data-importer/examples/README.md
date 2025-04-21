***REMOVED*** Data Importer Examples

This directory contains examples demonstrating how to use the `data-importer` package.

***REMOVED******REMOVED*** Logging Examples

***REMOVED******REMOVED******REMOVED*** Using the `@with_logging` Decorator

The `logging_example.py` demonstrates how to use the `@with_logging` decorator to easily add logging configuration to your functions:

```python
from data_importer.config import with_logging

@with_logging(log_level="DEBUG", log_dir=Path("./logs"), verbose=True)
def my_function():
    logger = logging.getLogger(__name__)
    logger.info("This will be logged")
    ***REMOVED*** Your function code here
```

***REMOVED******REMOVED******REMOVED*** Key Features of the Logging System

1. **Central Configuration**: All logging is configured through a single function
2. **Flexible Output**: Can log to both console and files
3. **Decorators**: Easy to apply with the `@with_logging` decorator
4. **Rich Console Output**: Uses different log levels for clear visualization

***REMOVED******REMOVED******REMOVED*** Configuring Logging Manually

If you need more control, you can also use the `configure_logging` function directly:

```python
from data_importer.config import configure_logging
from pathlib import Path

***REMOVED*** Configure logging at the start of your script
configure_logging(
    log_level="INFO",           ***REMOVED*** DEBUG, INFO, WARNING, ERROR
    log_dir=Path("./logs"),     ***REMOVED*** None for console-only logging
    verbose=True,               ***REMOVED*** Show debug messages in console
    quiet=False                 ***REMOVED*** Suppress console output except errors
)

***REMOVED*** Then use standard logging
import logging
logger = logging.getLogger(__name__)
logger.info("Application started")
logger.debug("This is a debug message")
logger.warning("Something unexpected happened")
logger.error("An error occurred")
```

***REMOVED******REMOVED******REMOVED*** Running the Examples

To run the logging example:

```bash
python examples/logging_example.py
```

This will demonstrate logging configuration with both the decorator and direct approaches.
