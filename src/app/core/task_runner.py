from typing import Callable

from src.app.core.logging import get_logger  # noqa: F401

logger = get_logger(__name__)


class TaskRunner:
    @staticmethod
    def run_in_bg(task: Callable, *args, **kwargs) -> None:

        try:
            result = task.delay(*args, **kwargs)
            logger.debug("Task sent!", id=result.id)
        except Exception as e:
            logger.error("Failed to send task", error=str(e), exc_info=True)
            raise


task_runner = TaskRunner()
