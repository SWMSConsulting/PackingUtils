### Run the API locally
```
cd api_packing
uvicorn api:app --reload
```

### Run the API using docker
- Build docker image and publish
```
cd api_packing
docker build -t packingsolver .

# (optional)
docker tag packingsolver harbor.swms-cloud.com/binpacking/packingsolver:latest
docker push harbor.swms-cloud.com/binpacking/packingsolver:latest
```

- Run the docker container 
```
docker run -p 8000:8000 packingsolver
```