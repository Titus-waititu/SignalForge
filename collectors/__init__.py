"""Collectors package for SignalForge"""
from .jobs.github_jobs import GitHubJobsCollector
from .jobs.remote_ok import RemoteOKCollector

__all__ = ["GitHubJobsCollector", "RemoteOKCollector"]
