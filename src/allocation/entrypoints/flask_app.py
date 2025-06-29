from typing import List, Tuple
from flask import Flask, request, Response

from datetime import datetime

from allocation.domain import model, commands
from allocation.service_layer.handlers import InvalidSku
from allocation.adapters import orm
from allocation.service_layer import messagebus, unit_of_work


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
        results = messagebus.handle(cmd, unit_of_work.SqlAlchemyUnitOfWork())
        batchref = results.pop(0)
    except InvalidSku as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201
