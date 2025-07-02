
import logging
import json

from dataclasses import asdict

from allocation import config
from allocation.domain import events

import redis


logger = logging.getLogger(__name__)


r = redis.Redis(**config.get_redis_host_and_port())


def publish(channel: str, event: events.Event) -> None:
    """Publish an event to the specified Redis channel."""
    logger.debug("Publishing: channel=%s, event=%s", channel, event)
    r.publish(channel, json.dumps(asdict(event)))
