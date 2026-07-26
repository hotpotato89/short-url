from taskiq_nats import PullBasedJetStreamBroker, PushBasedJetStreamBroker

from src.app.core.settings import settings


push_broker = PushBasedJetStreamBroker(
    servers=settings.nats.url,
    subject="taskiq_tasks"
)


pull_broker = PullBasedJetStreamBroker(
    servers=settings.nats.url,
    stream_name="short_url_stream",
    durable="short_url_durable",
    pull_consume_batch=5,
    subject="taskiq_tasks",
)
