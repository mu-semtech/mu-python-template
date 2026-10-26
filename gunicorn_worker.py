# Custom worker class for Gunicorn running Uvicorn against WSGI apps.
import asyncio
import sys

from gunicorn.arbiter import Arbiter
from uvicorn.middleware.wsgi import WSGIMiddleware
from uvicorn.server import Server
from uvicorn_worker import UvicornWorker


class UvicornWSGIWorker(UvicornWorker):
    """A Uvicorn worker for Gunicorn that serves a WSGI (Flask) application."""

    async def _serve(self) -> None:
        # gunicorn's threads setting determines how many requests a worker handles concurrently
        self.config.app = WSGIMiddleware(self.wsgi, workers=self.cfg.threads)
        server = Server(config=self.config)
        self._install_sigquit_handler()
        watcher = asyncio.create_task(self._exit_when_not_alive(server))
        await server.serve(sockets=self.sockets)
        watcher.cancel()
        if not server.started:
            sys.exit(Arbiter.WORKER_BOOT_ERROR)

    async def _exit_when_not_alive(self, server: Server) -> None:
        # gunicorn's reloader marks the worker as no longer alive, which uvicorn does not check by itself
        while self.alive:
            await asyncio.sleep(0.5)
        server.should_exit = True
