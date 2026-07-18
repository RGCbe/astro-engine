import sys
import os

# Ensure the root directory is on the python search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.main import app, jathagam, BirthData, translate_response_data, book_battle, CORPUS

def calculate_jathagam(data: BirthData):
    """Backwards-compatibility synchronous wrapper for the jathagam service."""
    import asyncio
    try:
        return asyncio.run(jathagam(data))
    except RuntimeError:
        # Handle case where event loop is already running (e.g. under uvicorn/pytest-asyncio)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(jathagam(data))


if __name__ == "__main__":
    import uvicorn
    # Use reload only when run directly in dev mode
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
