import pytest

from ..random_refs import random_sku, random_batch_ref, random_orderid

from . import api_client


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_202_and_batch_is_allocated() -> None:
    orderid = random_orderid()
    sku, othersku = random_sku(), random_sku("other")
    earlybatch = random_batch_ref("1")
    laterbatch = random_batch_ref("2")
    otherbatch = random_batch_ref("3")

    api_client.post_to_add_batch(laterbatch, sku, 100, "2011-01-02")
    api_client.post_to_add_batch(earlybatch, sku, 100, "2011-01-01")
    api_client.post_to_add_batch(otherbatch, othersku, 100, None)

    r = api_client.post_to_allocate(orderid, sku, 3)
    assert r.status_code == 202

    r = api_client.get_allocations(orderid)

    import pdb; pdb.set_trace()

    assert r.ok
    assert r.json() == [
        {
            "sku": sku,
            "batchref": earlybatch,
        }
    ]


@pytest.mark.usefixtures("postgres_db")
@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message() -> None:
    unknown_sku, orderid = random_sku(), random_orderid()

    r = api_client.post_to_allocate(orderid, unknown_sku, 20, expect_success=False)

    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"

    r = api_client.get_allocations(orderid)
    assert r.status_code == 404
