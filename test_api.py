import requests
import json
import copy
import os

from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.bin import Bin
from packutils.data.item import Item
from packutils.data.packer_configuration import PackerConfiguration
from packutils.data.position import Position
from packutils.data.packed_order import PackedOrder

from packutils.visual.packing_visualization import PackingVisualization

# HOST = "localhost"
HOST = "192.168.178.93"
PORT = 8000

PACKING_ENDPOINT = "variants"
# PACKING_ENDPOINT = "palletier"


def ping_api():
    request = f"http://{HOST}:{PORT}/"
    print(f"Request:    {request}")

    response = requests.get(request)
    body = json.loads(response.text)
    print(f"Response:   {body}")
    if response.status_code == 200 and body.get("status", None).lower() == "healthy":
        print("Server is up and running.")

    else:
        raise RuntimeError(
            "Cannot connect to server. Please check all parameters and the connection.")


def get_packing_variants(
    order: Order,
    baseConfig: PackerConfiguration,
    num_variants: int
):
    request = f"http://{HOST}:{PORT}/{PACKING_ENDPOINT}"
    print(f"Request:    {request}")
    orderDict = order.to_dict()
    orderDict["colli_details"] = {
        "width": 80, "length": 1, "height": 100, "max_collis": 10
    }
    data = {
        "order": orderDict,
        "num_variants": num_variants,
        "config": baseConfig.__dict__
    }
    print(f"Data:       {data}")
    response = requests.post(request, json=data)
    body = json.loads(response.text)
    if not response.status_code == 200:
        raise RuntimeError(f"Failed to get prediction. Reason: {body}")
    print(f"Response:   {body}")
    return body


ping_api()

articles = [
    Article("test1", width=26, length=1, height=16, amount=30),
    Article("test2", width=6, length=1, height=6, amount=11)
]
test_order = Order(order_id="test", articles=articles)

num_variants = 2
results = get_packing_variants(test_order,
                               baseConfig=PackerConfiguration(),
                               num_variants=num_variants)
print(len(results))
assert num_variants == len(results)
for result in results:
    packed = PackedOrder.from_dict(result)
    variant = packed.packing_variants[0]
