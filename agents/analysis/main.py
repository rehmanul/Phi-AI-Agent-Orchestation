"""
Analysis Agent Entry Point

Run with: python -m agents.analysis.main
"""

import asyncio

from agents.analysis.agent import AnalysisAgent
from agents.base import run_agent


if __name__ == "__main__":
    agent = AnalysisAgent()
    asyncio.run(run_agent(agent))
