from typing import List, Tuple
from flask import Flask, jsonify, request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime

from allocation import config
from allocation.domain import model
from allocation.adapters import orm, repository
from allocation.service_layer import services, unit_of_work


app = Flask(__name__)
orm.start_mappers()


def is_valid_sku(sku: str, batches: List[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


@app.route("/add_batch", methods=["POST"])
def add_batch() -> Tuple[Response, int]:
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        unit_of_work.SqlAlchemyUnitOfWork(),
    )
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint() -> Tuple[Response, int]:
    try:
        batch_ref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            unit_of_work.SqlAlchemyUnitOfWork(),
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({"message": str(e)}), 400
    return jsonify({"batchref": batch_ref}), 201

