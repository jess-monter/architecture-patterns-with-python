import uuid


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
