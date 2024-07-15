import uuid
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from schemas import ItemSchema, ItemUpdateSchema
from db import items

blueprint = Blueprint("Items", __name__, description="Operations on items")


@blueprint.route("/item/<string:item_id>")
class Item(MethodView):
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404, message="Item not found.")

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": "Item deleted."}
        except KeyError:
            abort(404, message="Item not found.")

    @blueprint.arguments(ItemUpdateSchema)
    def put(self, item_data, item_id):
        try:
            item = items[item_id]

            item |= item_data

            return item
        except KeyError:
            abort(404, message="Item not found.")


@blueprint.route("/item")
class ItemList(MethodView):
    def get(self):
        return {"items": list(items.values())}

    @blueprint.arguments(ItemSchema)
    def post(self, item_data):
        for item in items.values():
            if (
                item_data["name"] == item["name"]
                and item_data["store_id"] == item["store_id"]
            ):
                abort(400, message=f"Item already exists.")

        item_id = uuid.uuid4().hex
        item = {**item_data, "id": item_id}
        items[item_id] = item

        return item