# Custom worker class for Gunicorn running Uvicorn against WSGI apps.
import sys

from gunicorn.arbiter import Arbiter
from uvicorn.middleware.wsgi import WSGIMiddleware
from uvicorn.server import Server
from uvicorn.workers import UvicornWorker


class UvicornWSGIWorker(UvicornWorker):
    """A Uvicorn worker for Gunicorn that serves a WSGI (Flask) application."""

    async def _serve(self) -> None:
        self.config.app = WSGIMiddleware(self.wsgi)
        server = Server(config=self.config)
        self._install_sigquit_handler()
        await server.serve(sockets=self.sockets)
        if not server.started:
            sys.exit(Arbiter.WORKER_BOOT_ERROR)
