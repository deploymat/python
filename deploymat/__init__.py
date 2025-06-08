"""
PyDock - Python Docker Deployment Manager
Zarządza deploymentem aplikacji Docker Compose na VPS bez modyfikacji środowiska lokalnego.
"""

__version__ = "1.0.0"
__author__ = "PyDock Team"

from .core import PyDockManager
from .config import Config
from .deployment import Deployment
from .utils import Logger

__all__ = ['PyDockManager', 'Config', 'Deployment', 'Logger']