from taskiq_aio_pika import AioPikaBroker
from taskiq_aio_pika.queue import Queue
from taskiq.schedule_sources import LabelScheduleSource
from taskiq import TaskiqScheduler

from src.app.core.settings import settings

task_queue = Queue(name="short_url_tasks", durable=True)

dead_letter_queue = Queue(
    name="short_url_tasks_dlq",
    durable=True,
)


broker = AioPikaBroker(
    settings.rabbitmq.url,
    qos=10,
    task_queues=[task_queue],
    dead_letter_queue=dead_letter_queue,
)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)]
)
