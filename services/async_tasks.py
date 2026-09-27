"""
Background task executor for asynchronous non-blocking operations.

Used to offload:
  * Non-blocking SMTP email dispatches (eliminating 5-10s network latency)
  * Background Proof-of-Work mining and asynchronous verification tasks
"""
import atexit
import logging
from concurrent.futures import ThreadPoolExecutor
from flask import current_app

logger = logging.getLogger(__name__)

# Global thread pool for background worker jobs
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix='satyameva-worker')


def _shutdown_executor():
    try:
        _executor.shutdown(wait=False)
    except Exception:
        pass


atexit.register(_shutdown_executor)


def submit_task(fn, *args, **kwargs):
    """Submit a callable to the background thread pool."""
    try:
        return _executor.submit(fn, *args, **kwargs)
    except Exception as exc:
        logger.error("Failed to submit background task: %s", exc)
        return None


def submit_with_app_context(app, fn, *args, **kwargs):
    """
    Run a task in a background worker inside a Flask application context.
    """
    def _runner():
        with app.app_context():
            try:
                fn(*args, **kwargs)
            except Exception as exc:
                logger.error("Background task %s failed: %s", getattr(fn, '__name__', 'unnamed'), exc)

    return submit_task(_runner)
