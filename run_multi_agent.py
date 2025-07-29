#!/usr/bin/env python3
"""Run the multi-agent coaching system."""

import asyncio
from dotenv import load_dotenv
from src.interface.multi_agent_cli import main

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    asyncio.run(main())