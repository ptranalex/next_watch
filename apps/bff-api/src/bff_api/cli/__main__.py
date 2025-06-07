***REMOVED***!/usr/bin/env python
"""CLI main entry point for direct module execution.

This file allows the CLI to be run directly as a module:
python -m bff_api.cli
"""

import sys
from bff_api.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
