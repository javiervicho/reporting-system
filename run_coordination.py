#!/usr/bin/env python
"""
Script to run the CrewAI coordination system from the command line.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Make sure OpenAI API key is set
if "OPENAI_API_KEY" not in os.environ:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Please set it in your .env file or export it in your shell.")
    sys.exit(1)

# Import and run the CLI
from app.coordinator.cli import main

if __name__ == "__main__":
    main() 