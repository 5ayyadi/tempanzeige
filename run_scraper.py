#!/usr/bin/env python3
"""Production script to run the offers scraper."""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from runners.offers_scraper import main

if __name__ == "__main__":
    main()
