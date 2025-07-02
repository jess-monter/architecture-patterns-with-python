import pytest
import requests
from allocation import config

from ..random_refs import random_sku, random_batch_ref, random_orderid

from . import api_client


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch() -> None:
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batch_ref("1")
    laterbatch = random_batch_ref("2")
    otherbatch = random_batch_ref("3")

    api_client.post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    api_client.post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    api_client.post_to_add_batch(otherbatch, othersku, 100, None)

    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()["batchref"] == earlybatch


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message() -> None:
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {"orderid": orderid, "sku": unknown_sku, "qty": 20}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"

