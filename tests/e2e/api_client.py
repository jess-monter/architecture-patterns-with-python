from typing import Optional

import requests
from requests import Response
from allocation import config


def post_to_add_batch(ref: str, sku: str, qty: int, eta: Optional[str]) -> None:
    url = config.get_api_url()
    r = requests.post(
        f"{url}/add_batch", json={"ref": ref, "sku": sku, "qty": qty, "eta": eta}
    )
    assert r.status_code == 201


def post_to_allocate(orderid: str, sku: str, qty: int, expect_success: bool =True) -> Response:
    url = config.get_api_url()
    r = requests.post(
        f"{url}/allocate",
        json={
            "orderid": orderid,
            "sku": sku,
            "qty": qty,
        },
    )
    if expect_success:
        assert r.status_code == 201
    return r
