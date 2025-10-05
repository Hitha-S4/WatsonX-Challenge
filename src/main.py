import logging
import sys
import asyncio
import signal

from src.app import ProjectPlannerApp
from src.settings.app_settings import AppSettings


settings = AppSettings()

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def _exit_gracefully(
    sig: signal.Signals, loop: asyncio.AbstractEventLoop, app: ProjectPlannerApp
):
    """Cleanup tasks tied to the service's shutdown."""
    logger.info(f"Received exit signal {sig.name}...")

    await app.stop()
    await _exit_asyncio(loop=loop)


async def _exit_asyncio(loop: asyncio.AbstractEventLoop):
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    for task in tasks:
        task.cancel()

    logger.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


async def _setup_signal_handler(app: ProjectPlannerApp):
    logger.info("Setting up signal handlers")
    loop = asyncio.get_event_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(
                _exit_gracefully(sig=s, loop=loop, app=app)
            ),
        )


def _create_app(settings: AppSettings):
    try:
        return ProjectPlannerApp(settings=settings)
    except Exception as exception:
        logger.error(str(exception))
        sys.exit(-1)


async def _start():
    app = _create_app(settings=settings)
    try:
        await app.run()
        asyncio.create_task(_setup_signal_handler(app=app))
        logger.info("Registered all task")
    except Exception as exception:
        logger.error(str(exception))


def main():
    """main the first function called when app is started"""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop=loop)
    loop.create_task(_start())
    loop.run_forever()
    logger.info("Exiting...")


if __name__ == "__main__":
    main()