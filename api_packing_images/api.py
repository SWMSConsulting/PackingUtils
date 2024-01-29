from fastapi import FastAPI

from v1.api import api_v1

tags_metadata = [
    {
        "name": "v1",
        "description": "API version 1, visit /api/v1/docs for documentation.",
        "externalDocs": {
            "description": "Documentation",
            "url": "http://127.0.0.1/api/v1/docs",
        },
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.mount("/v1", api_v1)
