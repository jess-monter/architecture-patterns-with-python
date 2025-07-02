import json
import pytest

from tenacity import Retrying, stop_after_delay

from . import api_client, redis_client
from ..random_refs import random_sku, random_batch_ref, random_orderid


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
@pytest.mark.usefixtures("restart_redis_pubsub")
def test_change_batch_quantity_leading_to_reallocation() -> None:
    # Start with two batches and an order allocated to one of them
    order_id, sku = random_orderid(), random_sku()
    earlier_bathch, later_batch = random_batch_ref("earlier"), random_batch_ref("newer")
    
    api_client.post_to_add_batch(earlier_bathch, sku, qty=10, eta="2011-01-02")
    api_client.post_to_add_batch(later_batch, sku, qty=10, eta="2011-01-02")

    response = api_client.post_to_allocate(order_id, sku, qty=10)
    assert response.json()["batchref"] == earlier_bathch

    subscription = redis_client.subscribe_to("line_allocated")

    # Change quantity on allocated batch so it's less than our order
    redis_client.publish_message("change_batch_quantity", {"batchref": earlier_bathch, "qty": 5})

    # Wait until we see a message saying the order has been reallocated
    messages = []

    for attempt in Retrying(stop=stop_after_delay(3), reraise=True):
        with attempt:
            message = subscription.get_message(timeout=1)
            if message:
                messages.append(message)
                print(messages)
            data = json.loads(messages[-1]["data"])
            assert data["orderid"] == order_id
            assert data["batchref"] == later_batch
