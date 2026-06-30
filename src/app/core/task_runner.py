from typing import Callable
from src.app.core.celery import celery_app
import logging

logger = logging.getLogger(__name__)


class TaskRunner:
    @staticmethod
    def run_in_bg(task: Callable, *args, **kwargs) -> None:
        
        try:
            result = task.delay(*args, **kwargs)
            logger.debug(f"✅ Task sent! Task ID: {result.id}")
        except Exception as e:
            logger.error(f"❌ Failed to send task: {e}")
            raise


task_runner = TaskRunner()