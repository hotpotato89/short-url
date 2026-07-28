from collections.abc import Callable

from src.app.core.logging import get_logger
from src.app.core.taskiq_broker import *

logger = get_logger(__name__)


class TaskRunner:
    @staticmethod
    async def run_in_bg(task: Callable, *args, **kwargs) -> None:

        try:
            task_name = task.__name__
            await task.kiq(*args, **kwargs)
            logger.debug(
                "Task sent!",
                task=task_name,
                args=args,
                kwargs=kwargs,
            )
        except Exception as e:
            logger.exception(
                "Failed to send task",
                task=task.__name__,
                error=str(e),
            )
            raise


task_runner = TaskRunner()
