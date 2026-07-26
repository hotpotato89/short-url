from taskiq_nats import PullBasedJetStreamBroker

from src.app.core.settings import settings


broker = PullBasedJetStreamBroker(
    servers=settings.nats.url,
    stream_name="short_url_stream",
    durable="short_url_durable",
    pull_consume_batch=5,
    subject="taskiq_tasks",
)

