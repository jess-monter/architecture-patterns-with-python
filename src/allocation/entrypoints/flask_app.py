from typing import List, Tuple
from flask import Flask, request, Response, jsonify

from datetime import datetime


from allocation.domain import model, commands
from allocation.service_layer.handlers import InvalidSku
from allocation.adapters import orm
from allocation.service_layer import messagebus, unit_of_work
from allocation import views


app = Flask(__name__)
orm.start_mappers()


def is_valid_sku(sku: str, batches: List[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


@app.route("/add_batch", methods=["POST"])
def add_batch() -> Tuple[Response, int]:
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    cmd = commands.CreateBatch(
        request.json["ref"], request.json["sku"], request.json["qty"], eta
    )
    messagebus.handle(cmd, unit_of_work.SqlAlchemyUnitOfWork())
    return "OK", 201


@app.route("/allocate", methods=["POST"])
def allocate_endpoint() -> Tuple[Response, int]:
    try:
        cmd = commands.Allocate(
            request.json["orderid"], request.json["sku"], request.json["qty"]
        )
        messagebus.handle(cmd, unit_of_work.SqlAlchemyUnitOfWork())
    except InvalidSku as e:
        return {"message": str(e)}, 400
    return "OK", 202


@app.route("/allocations/<orderid>", methods=["GET"])
def allocations_view_endpoint(orderid: str) -> Tuple[Response, int]:
    uow = unit_of_work.SqlAlchemyUnitOfWork()
    results = views.allocations(orderid, uow)
    if not results:
        return "not found", 404
    return jsonify(results), 200
