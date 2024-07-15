import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores
from schemas import StoreSchema


blueprint = Blueprint("Stores", __name__, description="Operations on stores")


@blueprint.route("/store/<string:store_id>")
class Store(MethodView):
    def get(cls, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, message="Store not found.")

    def delete(cls, store_id):
        try:
            del stores[store_id]
            return {"message": "Store deleted."}
        except KeyError:
            abort(404, message="Store not found.")


@blueprint.route("/store")
class StoreList(MethodView):
    def get(cls):
        return {"stores": list(stores.values())}

    @blueprint.arguments(StoreSchema)
    def post(cls, store_data):
        for store in stores.values():
            if store_data["name"] == store["name"]:
                abort(400, message=f"Store already exists.")

        store_id = uuid.uuid4().hex
        store = {**store_data, "id": store_id}
        stores[store_id] = store

        return store