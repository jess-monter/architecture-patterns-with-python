from typing import List, Tuple
from flask import Flask, jsonify, request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from allocation import config
from allocation.domain import model
from allocation.adapters import orm, repository
from allocation.service_layer import services

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


def is_valid_sku(sku: str, batches: List[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


@app.route("/allocate", methods=["POST"])
def allocate_endpoint() -> Tuple[Response, int]:
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    line: model.OrderLine = model.OrderLine(
        orderid=request.json["orderid"],
        sku=request.json["sku"],
        qty=request.json["qty"]
    )

    try:
        batch_ref = services.allocate(line, repo, session)
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({"message": str(e)}), 400

    session.commit()
    return jsonify({"batchref": batch_ref}), 201
