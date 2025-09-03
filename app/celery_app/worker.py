from __future__ import annotations

from celery import Celery
from kombu import Exchange, Queue

from app.core.config import settings
from app.logging_config import setup_logging

setup_logging()

celery_app = Celery(
    "resumelab",
    broker=settings.RABBITMQ_URL,
    backend=None,  # we persist status in DB; no Celery result backend needed
    include=["app.celery_app.tasks"],  # register tasks without side-effect imports
)

# Reliability
celery_app.conf.update(
    task_time_limit=60,
    task_soft_time_limit=50,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_default_delivery_mode="persistent",
    # Exchanges / routing
    task_default_exchange="resumelab.direct",
    task_default_exchange_type="direct",
    task_default_routing_key="improve",
    task_default_queue="improve.q",
    # Publisher confirms
    broker_transport_options={"confirm_publish": True},
    # Queues
    task_queues=(
        Queue(
            name="improve.q",
            exchange=Exchange("resumelab.direct", type="direct", durable=True),
            routing_key="improve",
            durable=True,
            queue_arguments={
                "x-dead-letter-exchange": "resumelab.dlx",
                # optional TTL 15 minutes so stale tasks go to DLQ
                "x-message-ttl": 900_000,
            },
        ),
        Queue(
            name="improve.dlq",
            exchange=Exchange("resumelab.dlx", type="direct", durable=True),
            routing_key="improve",
            durable=True,
        ),
    ),
    task_routes={
        "improve_resume_task": {
            "queue": "improve.q",
            "routing_key": "improve",
            "exchange": "resumelab.direct",
        }
    },
    task_default_retry_delay=5,
    task_annotations={"*": {"max_retries": 3, "retry_backoff": True}},
)

# Eager for tests if configured
if settings.CELERY_TASK_ALWAYS_EAGER:
    celery_app.conf.task_always_eager = True


__all__ = ["celery_app"]
"""Celery application setup for background processing.

This module configures the Celery app (broker, queues, routing, reliability
options) used by the worker process. The app is imported by the `celery`
command via `-A app.celery_app.worker:celery_app`.
"""
