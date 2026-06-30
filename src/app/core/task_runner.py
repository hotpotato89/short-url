from typing import Callable


class TaskRunner:
    @staticmethod
    def run_in_bg(task: Callable, *args, **kwargs) -> None:
        task.delay(*args, **kwargs)


task_runner = TaskRunner()
