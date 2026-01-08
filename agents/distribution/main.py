"""Distribution Agent Entry Point"""
import asyncio
from agents.distribution.agent import DistributionAgent
from agents.base import run_agent

if __name__ == "__main__":
    asyncio.run(run_agent(DistributionAgent()))
