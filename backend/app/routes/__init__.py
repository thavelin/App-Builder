"""Routes package."""

# Export routers for easy importing
from . import generate, auth, websockets

__all__ = ['generate', 'auth', 'websockets']

