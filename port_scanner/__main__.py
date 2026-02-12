#!/usr/bin/env python3
"""
Entry point for running port_scanner as a module:
python3 -m port_scanner
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from port_scanner.main import main

if __name__ == "__main__":
    main()

