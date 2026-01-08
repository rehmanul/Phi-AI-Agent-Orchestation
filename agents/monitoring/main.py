"""
Monitoring Agent Entry Point

Run with: python -m agents.monitoring.main
"""

import asyncio

from agents.monitoring.agent import MonitoringAgent
from agents.base import run_agent


if __name__ == "__main__":
    agent = MonitoringAgent()
    asyncio.run(run_agent(agent))
