### Run the API locally

```bash
cd api_packing
uvicorn api:app --reload --port 9001
```

### Run the API using docker

- Build docker image and publish

```bash
cd api_packing
docker build -t packingsolver .
docker tag packingsolver harbor.swms-cloud.com/binpacking/packingsolver:1.0.20_dev3
docker push harbor.swms-cloud.com/binpacking/packingsolver:1.0.20_dev3
```

- Run the docker container

```bash
docker run -p 8000:8000 packingsolver
```
