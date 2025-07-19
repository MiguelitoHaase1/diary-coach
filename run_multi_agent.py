#!/usr/bin/env python3
"""Run the multi-agent coaching system."""

import asyncio
from src.interface.multi_agent_cli import main

if __name__ == "__main__":
    asyncio.run(main())