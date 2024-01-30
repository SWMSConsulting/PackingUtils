from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html

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

app = FastAPI(root_path="/api", openapi_tags=tags_metadata)

app.mount("/v1", api_v1)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(req: Request):
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API",
    )
