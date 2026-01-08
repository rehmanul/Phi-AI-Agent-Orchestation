"""Content Agent Entry Point"""
import asyncio
from agents.content.agent import ContentAgent
from agents.base import run_agent

if __name__ == "__main__":
    asyncio.run(run_agent(ContentAgent()))
