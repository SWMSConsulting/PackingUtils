from fastapi import FastAPI

from v1.api import api_v1


app = FastAPI(root_path="/api")

app.mount("/v1", api_v1)
