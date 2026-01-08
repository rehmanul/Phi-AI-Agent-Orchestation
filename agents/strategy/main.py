"""Strategy Agent Entry Point"""
import asyncio
from agents.strategy.agent import StrategyAgent
from agents.base import run_agent

if __name__ == "__main__":
    asyncio.run(run_agent(StrategyAgent()))
