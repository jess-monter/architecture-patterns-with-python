from typing import Callable

import uuid
import pytest
import requests
from allocation import config


def random_suffix() -> str:
    return uuid.uuid4().hex[:6]


def random_sku(name: str = "") -> str:
    """Generate a random SKU."""
    return f"sku-{name}-{random_suffix()}"


def random_batch_ref(name: str = "") -> str:
    """Generate a random batch reference."""
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name: str = "") -> str:
    """Generate a random order ID."""
    return f"order-{name}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_api_returns_allocation(add_stock: Callable) -> None:
    sku, other_sku = random_sku(), random_sku("other")
    early_batch = random_batch_ref("1")
    later_batch = random_batch_ref("2")
    other_batch = random_batch_ref("3")

    add_stock([
        (later_batch, sku, 100, "2011-01-02"),
        (early_batch, sku, 100, "2011-01-01"),
        (other_batch, other_sku, 100, None),
    ])
    data = {
        "orderid": random_orderid(),
        "sku": sku,
        "qty": 3,
    }
    url = config.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 201
    assert r.json()["batchref"] == early_batch

@pytest.mark.usefixtures("restart_api")
def test_allocations_are_persisted(add_stock: Callable) -> None:
    sku = random_sku()
    batch1, batch2 = random_batch_ref("1"), random_batch_ref("2")
    order1, order2 = random_orderid("1"), random_orderid("2")
    add_stock([
        (batch1, sku, 10, "2011-01-01"),
        (batch2, sku, 10, "2011-01-02"),
    ])
    line1 = {"orderid": order1, "sku": sku, "qty": 10}
    line2 = {"orderid": order2, "sku": sku, "qty": 10}

    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=line1)
    assert r.status_code == 201
    assert r.json()["batchref"] == batch1

    r = requests.post(f"{url}/allocate", json=line2)
    assert r.status_code == 201
    assert r.json()["batchref"] == batch2

@pytest.mark.usefixtures("restart_api")
def test_400_message_for_out_of_stock(add_stock: Callable) -> None:
    sku, small_batch, large_order = random_sku(), random_batch_ref("1"), random_orderid()
    add_stock([(small_batch, sku, 10, "2011-01-01")])
    data = {"orderid": large_order, "sku": sku, "qty": 20}

    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Out of stock for sku {sku}"

@pytest.mark.usefixtures("restart_api")
def test_400_message_for_invalid_sku() -> None:
    unknown_sku, order_id = random_sku(), random_orderid()
    data = {"orderid": order_id, "sku": unknown_sku, "qty": 20}
    url = config.get_api_url()
    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
