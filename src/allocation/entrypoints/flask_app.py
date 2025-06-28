from typing import List, Tuple
from flask import Flask, jsonify, request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime

from allocation import config
from allocation.domain import model
from allocation.adapters import orm, repository
from allocation.service_layer import services

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


def is_valid_sku(sku: str, batches: List[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


@app.route("/add_batch", methods=["POST"])
def add_batch() -> Tuple[Response, int]:
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        repo,
        session,
    )
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint() -> Tuple[Response, int]:
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    try:
        batch_ref = services.allocate(
            request.json["orderid"],
            request.json["sku"],
            request.json["qty"],
            repo,
            session
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    session.commit()
    return jsonify({"batchref": batch_ref}), 201
