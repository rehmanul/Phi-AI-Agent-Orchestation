"""Feedback Agent Entry Point"""
import asyncio
from agents.feedback.agent import FeedbackAgent
from agents.base import run_agent

if __name__ == "__main__":
    asyncio.run(run_agent(FeedbackAgent()))
