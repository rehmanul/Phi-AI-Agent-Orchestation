"""Tactics Agent Entry Point"""
import asyncio
from agents.tactics.agent import TacticsAgent
from agents.base import run_agent

if __name__ == "__main__":
    asyncio.run(run_agent(TacticsAgent()))
