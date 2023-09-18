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
docker tag packingsolver harbor.swms-cloud.com/binpacking/packingsolver:1.0
docker push harbor.swms-cloud.com/binpacking/packingsolver:1.0
```

- Run the docker container 
```
docker run -p 8000:8000 packingsolver
```