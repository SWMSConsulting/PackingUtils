import json
import requests

from packutils.data.order import Order
from packutils.data.article import Article
from packutils.data.packed_order import PackedOrder
from packutils.data.packer_configuration import PackerConfiguration
from packutils.visual.packing_visualization import PackingVisualization


HOST = "65.108.147.211"
# HOST = "localhost"
# HOST = "192.168.178.93"

PORT = 32795
# PORT = 8000

PACKING_ENDPOINT = "api/v1/variants"
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
            "Cannot connect to server. Please check all parameters and the connection."
        )


def get_packing_variants(
    order: Order, baseConfig: PackerConfiguration, num_variants: int
):
    request = f"http://{HOST}:{PORT}/api/v1/{PACKING_ENDPOINT}"
    print(f"Request:    {request}")
    orderDict = order.to_dict()
    orderDict["colli_details"] = {
        "width": 80,
        "length": 1,
        "height": 100,
        "max_collis": 10,
    }
    data = {
        "order": orderDict,
        "num_variants": num_variants,
        "config": baseConfig.__dict__,
    }

    data = """{"order":{"order_id":"467139","articles":[{"id":"70171000","width":68.0,"length":1.0,"height":68.0,"weight":3.5,"amount":10},{"id":"71610126","width":68.0,"length":1.0,"height":68.0,"weight":0.0,"amount":2}],"supplies":[],"colli_details":{"width":800.0,"length":1.0,"height":600.0,"max_collis":10}}}"""
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
    Article("test2", width=6, length=1, height=6, amount=11),
]
test_order = Order(order_id="test", articles=articles)

num_variants = 2
result = get_packing_variants(
    test_order, baseConfig=PackerConfiguration(), num_variants=num_variants
)
packed = PackedOrder.from_dict(result.get("packed_order", {}))
print(len(packed.packing_variants))
assert num_variants == len(packed.packing_variants)

vis = PackingVisualization()
for variant, cfg in zip(packed.packing_variants, result.get("configs")):
    print(cfg)
    # vis.visualize_packing_variant(variant)
